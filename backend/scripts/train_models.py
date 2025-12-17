"""
Script to train and save recommendation models.
Run: python scripts/train_models.py
"""
import os
import sys
import pickle
import pandas as pd
import numpy as np
from datetime import datetime
from tqdm import tqdm

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient


def connect_mongodb(uri='mongodb://localhost:27017', db_name='movie_recommendation'):
    """Connect to MongoDB."""
    client = MongoClient(uri)
    db = client[db_name]
    client.admin.command('ping')
    print(f"✓ Connected to MongoDB: {db_name}")
    return db


def load_data_from_mongodb(db):
    """Load data from MongoDB into DataFrames."""
    print("\nLoading data from MongoDB...")
    
    # Load movies
    movies_cursor = db.movies.find({})
    movies_df = pd.DataFrame(list(movies_cursor))
    print(f"  Movies: {len(movies_df):,}")
    
    # Load ratings
    ratings_cursor = db.ratings.find({})
    ratings_df = pd.DataFrame(list(ratings_cursor))
    print(f"  Ratings: {len(ratings_df):,}")
    
    # Filter to only movies with ratings
    rated_movie_ids = set(ratings_df['movieId'].unique())
    movies_df = movies_df[movies_df['movieId'].isin(rated_movie_ids)]
    print(f"  Movies with ratings: {len(movies_df):,}")
    
    return movies_df, ratings_df


def train_content_based(movies_df, ratings_df, save_path):
    """Train content-based model."""
    print("\n" + "=" * 50)
    print("Training Content-Based Model")
    print("=" * 50)
    
    from app.models.content_based import ContentBasedModel
    from app.services.vectorization import Vectorizer
    
    # Create TF-IDF vectors
    print("Creating TF-IDF vectors...")
    vectorizer = Vectorizer()
    genres_list = movies_df['genres'].tolist()
    tfidf_matrix, _ = vectorizer.tfidf_vectorize(genres_list)
    
    # Fit model
    print(f"Fitting model with {len(movies_df)} movies...")
    model = ContentBasedModel()
    model.fit(movies_df, tfidf_matrix=tfidf_matrix)
    
    print(f"  Similarity matrix shape: {model.similarity_matrix.shape}")
    
    # Save model
    with open(save_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"✓ Model saved to: {save_path}")
    
    return model


def train_item_based(movies_df, ratings_df, save_path):
    """Train item-based collaborative filtering model."""
    print("\n" + "=" * 50)
    print("Training Item-Based Model")
    print("=" * 50)
    
    from app.models.item_based import ItemBasedModel
    
    # Fit model
    print("Fitting model (this may take a while)...")
    model = ItemBasedModel(k=20, min_ratings=10)  # Increase min_ratings to reduce matrix size
    model.fit(ratings_df, movies_df)
    
    print(f"  Items in model: {len(model.movie_ids)}")
    
    # Save model
    with open(save_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"✓ Model saved to: {save_path}")
    
    return model


def train_user_based(movies_df, ratings_df, save_path):
    """Train user-based collaborative filtering model."""
    print("\n" + "=" * 50)
    print("Training User-Based Model")
    print("=" * 50)
    
    from app.models.user_based import UserBasedModel
    
    # Fit model
    print("Fitting model (this may take a while)...")
    model = UserBasedModel(k=20, min_common=3)
    model.fit(ratings_df, movies_df)
    
    print(f"  Users in model: {len(model.user_ids)}")
    
    # Save model
    with open(save_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"✓ Model saved to: {save_path}")
    
    return model


def train_hybrid(movies_df, ratings_df, content_model, item_model, user_model, save_path):
    """Train hybrid model."""
    print("\n" + "=" * 50)
    print("Training Hybrid Model")
    print("=" * 50)
    
    from app.models.hybrid import HybridModel
    
    # Create model with pre-trained components
    print("Creating hybrid model...")
    model = HybridModel(content_weight=0.3, item_weight=0.35, user_weight=0.35)
    model.fit(movies_df, ratings_df, 
              content_model=content_model,
              item_model=item_model,
              user_model=user_model)
    
    # Save model
    with open(save_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"✓ Model saved to: {save_path}")
    
    return model


def evaluate_models(models, test_df, train_df, db, movies_df):
    """Evaluate all models and save metrics to MongoDB."""
    print("\n" + "=" * 50)
    print("Evaluating Models")
    print("=" * 50)
    
    from app.services.evaluation import ModelEvaluator
    
    for model_name, model in models.items():
        print(f"\nEvaluating {model_name}...")
        
        try:
            metrics = {
                'rmse': 0.0,
                'mae': 0.0,
                'precision@5': 0.0,
                'precision@10': 0.0,
                'recall@5': 0.0,
                'recall@10': 0.0
            }
            
            # Sample test for evaluation
            sample_users = test_df['userId'].unique()[:50]
            
            y_true = []
            y_pred = []
            
            for user_id in tqdm(sample_users, desc=f"Testing {model_name}"):
                user_test = test_df[test_df['userId'] == user_id]
                user_train = train_df[train_df['userId'] == user_id]
                
                # Get user's training ratings for content-based
                user_rated = [
                    {'movieId': int(r['movieId']), 'rating': float(r['rating'])}
                    for _, r in user_train.iterrows()
                ]
                
                for _, row in user_test.head(5).iterrows():  # Limit per user
                    pred = None
                    if model_name == 'content_based':
                        pred = model.predict_rating(user_id, row['movieId'], user_rated)
                    elif model_name == 'hybrid':
                        pred = model.predict_rating(user_id, row['movieId'], user_rated)
                    else:
                        pred = model.predict_rating(user_id, row['movieId'])
                    
                    if pred is not None:
                        y_true.append(row['rating'])
                        y_pred.append(pred)
            
            if y_true and y_pred:
                metrics['rmse'] = ModelEvaluator.rmse(np.array(y_true), np.array(y_pred))
                metrics['mae'] = ModelEvaluator.mae(np.array(y_true), np.array(y_pred))
            
            print(f"  Predictions: {len(y_pred)}")
            print(f"  RMSE: {metrics['rmse']:.4f}")
            print(f"  MAE:  {metrics['mae']:.4f}")
            
            # Save to MongoDB
            db.models.update_one(
                {'modelName': model_name},
                {
                    '$set': {
                        'modelName': model_name,
                        'version': '1.0',
                        'metrics': metrics,
                        'trainedAt': datetime.utcnow(),
                        'isActive': True
                    }
                },
                upsert=True
            )
            print(f"  ✓ Metrics saved to MongoDB")
            
        except Exception as e:
            print(f"  Error evaluating {model_name}: {e}")
            import traceback
            traceback.print_exc()


def main():
    print("=" * 60)
    print("Model Training Script")
    print("=" * 60)
    
    # Setup paths
    models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models_saved')
    os.makedirs(models_dir, exist_ok=True)
    
    # Connect to MongoDB
    try:
        db = connect_mongodb()
    except Exception as e:
        print(f"\n❌ Cannot connect to MongoDB: {e}")
        return
    
    # Load data
    movies_df, ratings_df = load_data_from_mongodb(db)
    
    if len(movies_df) == 0 or len(ratings_df) == 0:
        print("Error: No data found. Run import_to_mongodb.py first.")
        return
    
    # Split data for evaluation (80/20)
    print("\nSplitting data...")
    from sklearn.model_selection import train_test_split
    train_df, test_df = train_test_split(ratings_df, test_size=0.2, random_state=42)
    print(f"  Train: {len(train_df):,} ratings")
    print(f"  Test:  {len(test_df):,} ratings")
    
    # Train models
    models = {}
    
    content_model = train_content_based(
        movies_df, train_df, 
        os.path.join(models_dir, 'content_based.pkl')
    )
    models['content_based'] = content_model
    
    item_model = train_item_based(
        movies_df, train_df,
        os.path.join(models_dir, 'item_based.pkl')
    )
    models['item_based'] = item_model
    
    user_model = train_user_based(
        movies_df, train_df,
        os.path.join(models_dir, 'user_based.pkl')
    )
    models['user_based'] = user_model
    
    hybrid_model = train_hybrid(
        movies_df, train_df,
        content_model, item_model, user_model,
        os.path.join(models_dir, 'hybrid.pkl')
    )
    models['hybrid'] = hybrid_model
    
    # Evaluate models
    evaluate_models(models, test_df, train_df, db, movies_df)
    
    # Summary
    print("\n" + "=" * 60)
    print("Training Summary")
    print("=" * 60)
    print(f"Models saved to: {models_dir}")
    for name in models:
        path = os.path.join(models_dir, f'{name}.pkl')
        size_mb = os.path.getsize(path) / 1024 / 1024
        print(f"  ✓ {name}.pkl ({size_mb:.1f} MB)")
    print("=" * 60)
    print("\n✓ Training completed successfully!")


if __name__ == '__main__':
    main()
