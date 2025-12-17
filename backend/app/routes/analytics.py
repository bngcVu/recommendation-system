"""
API routes for analytics and data visualization.
"""
from flask import Blueprint, request, jsonify
from app.database.connection import MongoDB, Collections
from typing import Dict, List

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/analytics/stats', methods=['GET'])
def get_stats():
    """Get overall statistics."""
    try:
        movies_col = MongoDB.get_collection(Collections.MOVIES)
        users_col = MongoDB.get_collection(Collections.USERS)
        ratings_col = MongoDB.get_collection(Collections.RATINGS)
        
        if movies_col is None:
            return jsonify(_get_mock_stats())
        
        # Count totals
        total_movies = movies_col.count_documents({})
        total_users = users_col.count_documents({}) if users_col is not None else 0
        total_ratings = ratings_col.count_documents({}) if ratings_col is not None else 0
        
        # Calculate average rating
        avg_rating = 3.5
        if ratings_col is not None:
            pipeline = [{'$group': {'_id': None, 'avgRating': {'$avg': '$rating'}}}]
            result = list(ratings_col.aggregate(pipeline))
            if result:
                avg_rating = round(result[0]['avgRating'], 2)
        
        return jsonify({
            'totalMovies': total_movies,
            'totalUsers': total_users,
            'totalRatings': total_ratings,
            'avgRating': avg_rating
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/analytics/rating-distribution', methods=['GET'])
def get_rating_distribution():
    """Get rating distribution histogram data."""
    try:
        collection = MongoDB.get_collection(Collections.RATINGS)
        
        if collection is None:
            return jsonify({'distribution': _get_mock_rating_distribution()})
        
        # Aggregate rating counts
        pipeline = [
            {'$group': {'_id': '$rating', 'count': {'$sum': 1}}},
            {'$sort': {'_id': 1}}
        ]
        
        result = list(collection.aggregate(pipeline))
        distribution = [{'rating': doc['_id'], 'count': doc['count']} for doc in result]
        
        return jsonify({'distribution': distribution})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/analytics/top-movies', methods=['GET'])
def get_top_movies():
    """Get top rated movies for analytics."""
    try:
        limit = min(int(request.args.get('limit', 10)), 50)
        min_ratings = int(request.args.get('min_ratings', 50))
        
        collection = MongoDB.get_collection(Collections.MOVIES)
        
        if collection is None:
            return jsonify({'movies': _get_mock_top_movies(limit)})
        
        cursor = collection.find(
            {'ratingCount': {'$gte': min_ratings}}
        ).sort([('avgRating', -1), ('ratingCount', -1)]).limit(limit)
        
        movies = []
        for doc in cursor:
            movies.append({
                'movieId': doc.get('movieId'),
                'title': doc.get('title', ''),
                'avgRating': float(doc.get('avgRating', 0)),
                'ratingCount': int(doc.get('ratingCount', 0))
            })
        
        return jsonify({'movies': movies})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/analytics/genre-frequency', methods=['GET'])
def get_genre_frequency():
    """Get genre frequency for bar chart."""
    try:
        collection = MongoDB.get_collection(Collections.MOVIES)
        
        if collection is None:
            return jsonify({'genres': _get_mock_genre_frequency()})
        
        # Unwind genres and count
        pipeline = [
            {'$unwind': '$genres'},
            {'$group': {'_id': '$genres', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 15}
        ]
        
        result = list(collection.aggregate(pipeline))
        genres = [{'genre': doc['_id'], 'count': doc['count']} for doc in result]
        
        return jsonify({'genres': genres})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/analytics/heatmap', methods=['GET'])
def get_rating_heatmap():
    """Get sample rating heatmap data (user x movie matrix)."""
    try:
        n_users = min(int(request.args.get('n_users', 20)), 50)
        n_movies = min(int(request.args.get('n_movies', 20)), 50)
        
        collection = MongoDB.get_collection(Collections.RATINGS)
        
        if collection is None:
            return jsonify(_get_mock_heatmap_data(n_users, n_movies))
        
        # Get sample of most active users
        user_pipeline = [
            {'$group': {'_id': '$userId', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': n_users}
        ]
        top_users = [doc['_id'] for doc in collection.aggregate(user_pipeline)]
        
        # Get most rated movies
        movie_pipeline = [
            {'$group': {'_id': '$movieId', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': n_movies}
        ]
        top_movies = [doc['_id'] for doc in collection.aggregate(movie_pipeline)]
        
        # Get ratings for these users/movies
        ratings = collection.find({
            'userId': {'$in': top_users},
            'movieId': {'$in': top_movies}
        })
        
        # Build matrix
        matrix = {}
        for rating in ratings:
            user_id = rating['userId']
            movie_id = rating['movieId']
            if user_id not in matrix:
                matrix[user_id] = {}
            matrix[user_id][movie_id] = rating['rating']
        
        return jsonify({
            'userIds': top_users,
            'movieIds': top_movies,
            'matrix': matrix
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/analytics/user-activity', methods=['GET'])
def get_user_activity():
    """Get user activity distribution."""
    try:
        collection = MongoDB.get_collection(Collections.RATINGS)
        
        if collection is None:
            return jsonify({'distribution': _get_mock_user_activity()})
        
        # Count ratings per user and group by ranges
        pipeline = [
            {'$group': {'_id': '$userId', 'ratingCount': {'$sum': 1}}},
            {'$bucket': {
                'groupBy': '$ratingCount',
                'boundaries': [0, 10, 50, 100, 500, 1000, 10000],
                'default': '10000+',
                'output': {'count': {'$sum': 1}}
            }}
        ]
        
        result = list(collection.aggregate(pipeline))
        distribution = [{'range': str(doc['_id']), 'count': doc['count']} for doc in result]
        
        return jsonify({'distribution': distribution})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Mock data functions
def _get_mock_stats() -> Dict:
    return {
        'totalMovies': 10000,
        'totalUsers': 50000,
        'totalRatings': 1000000,
        'avgRating': 3.52
    }


def _get_mock_rating_distribution() -> List[Dict]:
    return [
        {'rating': 0.5, 'count': 5234},
        {'rating': 1.0, 'count': 12453},
        {'rating': 1.5, 'count': 18976},
        {'rating': 2.0, 'count': 45678},
        {'rating': 2.5, 'count': 78934},
        {'rating': 3.0, 'count': 156789},
        {'rating': 3.5, 'count': 234567},
        {'rating': 4.0, 'count': 289876},
        {'rating': 4.5, 'count': 123456},
        {'rating': 5.0, 'count': 34037},
    ]


def _get_mock_top_movies(limit: int) -> List[Dict]:
    movies = [
        {'movieId': 1, 'title': 'The Shawshank Redemption (1994)', 'avgRating': 4.8, 'ratingCount': 12453},
        {'movieId': 2, 'title': 'The Godfather (1972)', 'avgRating': 4.7, 'ratingCount': 9821},
        {'movieId': 3, 'title': 'The Dark Knight (2008)', 'avgRating': 4.6, 'ratingCount': 15234},
        {'movieId': 11, 'title': 'The Lord of the Rings (2001)', 'avgRating': 4.6, 'ratingCount': 14532},
        {'movieId': 5, 'title': 'Forrest Gump (1994)', 'avgRating': 4.5, 'ratingCount': 11234},
        {'movieId': 4, 'title': 'Pulp Fiction (1994)', 'avgRating': 4.5, 'ratingCount': 8932},
        {'movieId': 6, 'title': 'Inception (2010)', 'avgRating': 4.4, 'ratingCount': 13456},
        {'movieId': 7, 'title': 'The Matrix (1999)', 'avgRating': 4.4, 'ratingCount': 10234},
        {'movieId': 12, 'title': 'Star Wars (1977)', 'avgRating': 4.4, 'ratingCount': 11234},
        {'movieId': 8, 'title': 'Goodfellas (1990)', 'avgRating': 4.3, 'ratingCount': 7654},
    ]
    return movies[:limit]


def _get_mock_genre_frequency() -> List[Dict]:
    return [
        {'genre': 'Drama', 'count': 4532},
        {'genre': 'Comedy', 'count': 3421},
        {'genre': 'Action', 'count': 2876},
        {'genre': 'Thriller', 'count': 2345},
        {'genre': 'Romance', 'count': 1987},
        {'genre': 'Adventure', 'count': 1654},
        {'genre': 'Sci-Fi', 'count': 1432},
        {'genre': 'Horror', 'count': 1234},
        {'genre': 'Crime', 'count': 1098},
        {'genre': 'Fantasy', 'count': 876},
    ]


def _get_mock_heatmap_data(n_users: int, n_movies: int) -> Dict:
    import random
    user_ids = list(range(1, n_users + 1))
    movie_ids = list(range(1, n_movies + 1))
    
    matrix = {}
    for uid in user_ids:
        matrix[uid] = {}
        for mid in random.sample(movie_ids, random.randint(3, min(10, n_movies))):
            matrix[uid][mid] = round(random.uniform(1, 5) * 2) / 2  # 0.5 increments
    
    return {'userIds': user_ids, 'movieIds': movie_ids, 'matrix': matrix}


def _get_mock_user_activity() -> List[Dict]:
    return [
        {'range': '1-10', 'count': 25000},
        {'range': '11-50', 'count': 15000},
        {'range': '51-100', 'count': 6000},
        {'range': '101-500', 'count': 3000},
        {'range': '501-1000', 'count': 800},
        {'range': '1000+', 'count': 200},
    ]
