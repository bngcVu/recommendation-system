"""
Optimized script to import CSV data into MongoDB.
Uses batch processing without iterrows for much better performance.
Run: python scripts/import_to_mongodb.py [--limit N]
"""
import os
import sys
import argparse
import pandas as pd
from datetime import datetime
from tqdm import tqdm

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient


def parse_args():
    parser = argparse.ArgumentParser(description='Import data to MongoDB')
    parser.add_argument('--limit', type=int, default=None, 
                        help='Limit number of ratings to import (for testing)')
    parser.add_argument('--uri', type=str, default='mongodb://localhost:27017',
                        help='MongoDB URI')
    parser.add_argument('--db', type=str, default='movie_recommendation',
                        help='Database name')
    return parser.parse_args()


def connect_mongodb(uri, db_name):
    """Connect to MongoDB."""
    client = MongoClient(uri)
    db = client[db_name]
    client.admin.command('ping')
    print(f"✓ Connected to MongoDB: {db_name}")
    return db


def parse_genres(genres_str):
    """Parse genres string to list."""
    if pd.isna(genres_str) or genres_str == '(no genres listed)':
        return []
    return [g.strip() for g in str(genres_str).split('|') if g.strip()]


def extract_year(title):
    """Extract year from title."""
    import re
    match = re.search(r'\((\d{4})\)\s*$', str(title))
    return int(match.group(1)) if match else None


def import_movies(db, movies_df):
    """Import movies using vectorized operations."""
    print(f"\nImporting {len(movies_df)} movies...")
    
    # Clear existing
    db.movies.delete_many({})
    
    # Process data using vectorized operations
    movies_df = movies_df.copy()
    movies_df['genres'] = movies_df['genres'].apply(parse_genres)
    movies_df['year'] = movies_df['title'].apply(extract_year)
    movies_df['avgRating'] = 0.0
    movies_df['ratingCount'] = 0
    
    now = datetime.utcnow()
    movies_df['createdAt'] = now
    movies_df['updatedAt'] = now
    
    # Convert to records
    records = movies_df.to_dict('records')
    
    # Insert in batches
    batch_size = 5000
    for i in tqdm(range(0, len(records), batch_size), desc="Inserting movies"):
        batch = records[i:i + batch_size]
        db.movies.insert_many(batch)
    
    print(f"✓ Imported {len(records)} movies")


def import_ratings(db, ratings_df, limit=None):
    """Import ratings using optimized batch processing."""
    if limit:
        ratings_df = ratings_df.head(limit)
        print(f"\nImporting {len(ratings_df)} ratings (limited)...")
    else:
        print(f"\nImporting {len(ratings_df)} ratings...")
    
    # Clear existing
    db.ratings.delete_many({})
    
    # Convert timestamp
    if 'timestamp' in ratings_df.columns:
        ratings_df = ratings_df.copy()
        ratings_df['timestamp'] = pd.to_datetime(ratings_df['timestamp'], unit='s')
    
    # Add createdAt
    ratings_df['createdAt'] = datetime.utcnow()
    
    # Convert to records and insert in batches
    batch_size = 100000  # Larger batches for speed
    total_batches = (len(ratings_df) + batch_size - 1) // batch_size
    
    for i in tqdm(range(0, len(ratings_df), batch_size), desc="Inserting ratings", total=total_batches):
        batch_df = ratings_df.iloc[i:i + batch_size]
        records = batch_df.to_dict('records')
        db.ratings.insert_many(records)
    
    print(f"✓ Imported {len(ratings_df)} ratings")


def update_movie_stats(db):
    """Calculate and update average ratings for movies."""
    print("\nCalculating movie statistics...")
    
    pipeline = [
        {'$group': {
            '_id': '$movieId',
            'avgRating': {'$avg': '$rating'},
            'ratingCount': {'$sum': 1}
        }}
    ]
    
    results = list(tqdm(db.ratings.aggregate(pipeline, allowDiskUse=True), desc="Aggregating"))
    
    # Batch update using bulk operations
    from pymongo import UpdateOne
    
    batch_size = 5000
    for i in tqdm(range(0, len(results), batch_size), desc="Updating movie stats"):
        batch = results[i:i + batch_size]
        operations = [
            UpdateOne(
                {'movieId': stat['_id']},
                {'$set': {
                    'avgRating': round(stat['avgRating'], 2),
                    'ratingCount': stat['ratingCount'],
                    'updatedAt': datetime.utcnow()
                }}
            )
            for stat in batch
        ]
        db.movies.bulk_write(operations)
    
    print(f"✓ Updated stats for {len(results)} movies")


def create_users(db, ratings_df, movies_df):
    """Create user profiles from ratings using optimized groupby."""
    print("\nCreating user profiles...")
    
    # Clear existing
    db.users.delete_many({})
    
    # Get unique users
    user_ids = ratings_df['userId'].unique()
    print(f"  Found {len(user_ids)} unique users")
    
    # Group ratings by user
    user_ratings = ratings_df.groupby('userId').agg({
        'movieId': list,
        'rating': 'mean'
    }).reset_index()
    user_ratings.columns = ['userId', 'ratedMovies', 'avgRating']
    
    # Create movie-genres lookup
    movie_genres = dict(zip(movies_df['movieId'], movies_df['genres']))
    
    # Process users in batches
    users_data = []
    for _, row in tqdm(user_ratings.iterrows(), total=len(user_ratings), desc="Processing users"):
        user_id = int(row['userId'])
        rated_movies = [int(m) for m in row['ratedMovies']]
        
        # Get favorite genres
        all_genres = []
        for mid in rated_movies[:50]:  # Sample for efficiency
            if mid in movie_genres:
                genres = movie_genres[mid]
                if isinstance(genres, list):
                    all_genres.extend(genres)
        
        genre_counts = pd.Series(all_genres).value_counts()
        favorite_genres = genre_counts.head(5).index.tolist() if len(genre_counts) > 0 else []
        
        users_data.append({
            'userId': user_id,
            'username': f'user_{user_id}',
            'ratedMovies': rated_movies,
            'watchedMovies': rated_movies,
            'preferences': {
                'favoriteGenres': favorite_genres,
                'avgRating': round(float(row['avgRating']), 2)
            },
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow()
        })
    
    # Insert in batches
    batch_size = 5000
    for i in tqdm(range(0, len(users_data), batch_size), desc="Inserting users"):
        batch = users_data[i:i + batch_size]
        db.users.insert_many(batch)
    
    print(f"✓ Created {len(users_data)} user profiles")


def create_indices(db):
    """Create database indices."""
    print("\nCreating indices...")
    
    db.movies.create_index("movieId", unique=True)
    db.movies.create_index("genres")
    db.movies.create_index([("avgRating", -1)])
    db.movies.create_index([("title", "text")])
    
    db.users.create_index("userId", unique=True)
    
    db.ratings.create_index([("userId", 1), ("movieId", 1)], unique=True)
    db.ratings.create_index("movieId")
    db.ratings.create_index([("timestamp", -1)])
    
    print("✓ Indices created")


def main():
    args = parse_args()
    
    print("=" * 60)
    print("MongoDB Data Import Script (Optimized)")
    print("=" * 60)
    
    if args.limit:
        print(f"Note: Limiting ratings to {args.limit:,}")
    
    # Paths
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'raw')
    movies_path = os.path.join(data_dir, 'movies.csv')
    ratings_path = os.path.join(data_dir, 'ratings.csv')
    
    # Check files
    if not os.path.exists(movies_path) or not os.path.exists(ratings_path):
        print("Error: CSV files not found. Run download_data.py first.")
        return
    
    # Load CSV files
    print("\nLoading CSV files...")
    movies_df = pd.read_csv(movies_path)
    print(f"  Movies: {len(movies_df):,} rows")
    
    ratings_df = pd.read_csv(ratings_path)
    print(f"  Ratings: {len(ratings_df):,} rows")
    
    # Connect to MongoDB
    try:
        db = connect_mongodb(args.uri, args.db)
    except Exception as e:
        print(f"\n❌ Cannot connect to MongoDB: {e}")
        print("\nMake sure MongoDB is running:")
        print("  docker-compose up -d")
        return
    
    # Import data
    import_movies(db, movies_df)
    import_ratings(db, ratings_df, limit=args.limit)
    update_movie_stats(db)
    create_users(db, ratings_df if not args.limit else ratings_df.head(args.limit), movies_df)
    create_indices(db)
    
    # Summary
    print("\n" + "=" * 60)
    print("Import Summary")
    print("=" * 60)
    print(f"  Movies:  {db.movies.count_documents({}):,}")
    print(f"  Ratings: {db.ratings.count_documents({}):,}")
    print(f"  Users:   {db.users.count_documents({}):,}")
    print("=" * 60)
    print("\n✓ Data import completed successfully!")


if __name__ == '__main__':
    main()
