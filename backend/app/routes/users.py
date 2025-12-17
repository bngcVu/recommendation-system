"""
API routes for user management.
"""
from flask import Blueprint, request, jsonify
from app.database.connection import MongoDB, Collections
from datetime import datetime
from typing import Dict, List


users_bp = Blueprint('users', __name__)


@users_bp.route('/users', methods=['GET'])
def get_users():
    """Get list of users with pagination."""
    try:
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 20)), 100)
        
        collection = MongoDB.get_collection(Collections.USERS)
        
        if collection is None:
            return jsonify(_get_mock_users())
        
        skip = (page - 1) * limit
        cursor = collection.find().skip(skip).limit(limit)
        
        users = [_serialize_user(doc) for doc in cursor]
        total = collection.count_documents({})
        
        return jsonify({
            'users': users,
            'page': page,
            'limit': limit,
            'total': total
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id: int):
    """Get a single user by ID."""
    try:
        collection = MongoDB.get_collection(Collections.USERS)
        
        if collection is None:
            mock = _get_mock_user(user_id)
            if mock:
                return jsonify(mock)
            return jsonify({'error': 'User not found'}), 404
        
        user = collection.find_one({'userId': user_id})
        
        if user is None:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify(_serialize_user(user))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/users/<int:user_id>/history', methods=['GET'])
def get_user_history(user_id: int):
    """Get user's rating history."""
    try:
        limit = min(int(request.args.get('limit', 50)), 100)
        
        ratings_col = MongoDB.get_collection(Collections.RATINGS)
        movies_col = MongoDB.get_collection(Collections.MOVIES)
        
        if ratings_col is None:
            return jsonify(_get_mock_user_history(user_id, limit))
        
        # Get user's ratings
        cursor = ratings_col.find({'userId': user_id}).sort('timestamp', -1).limit(limit)
        
        history = []
        for rating in cursor:
            movie_info = {'movieId': rating['movieId'], 'title': f"Movie {rating['movieId']}"}
            
            if movies_col is not None:
                movie = movies_col.find_one({'movieId': rating['movieId']})
                if movie:
                    movie_info = {
                        'movieId': movie['movieId'],
                        'title': movie.get('title', ''),
                        'genres': movie.get('genres', []),
                        'avgRating': float(movie.get('avgRating', 0))
                    }
            
            history.append({
                **movie_info,
                'userRating': float(rating['rating']),
                'timestamp': rating.get('timestamp', datetime.utcnow()).isoformat()
            })
        
        return jsonify({'userId': user_id, 'history': history})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/users/<int:user_id>/watch-history', methods=['GET'])
def get_watch_history(user_id: int):
    """Get user's watch history (movies they've watched)."""
    try:
        limit = min(int(request.args.get('limit', 50)), 100)
        
        watch_col = MongoDB.get_collection(Collections.WATCH_HISTORY)
        movies_col = MongoDB.get_collection(Collections.MOVIES)
        
        if watch_col is None:
            return jsonify({'userId': user_id, 'watchHistory': []})
        
        cursor = watch_col.find({'userId': user_id}).sort('watchedAt', -1).limit(limit)
        
        watch_history = []
        for item in cursor:
            movie_info = {'movieId': item['movieId']}
            
            if movies_col is not None:
                movie = movies_col.find_one({'movieId': item['movieId']})
                if movie:
                    movie_info.update({
                        'title': movie.get('title', ''),
                        'genres': movie.get('genres', []),
                        'avgRating': float(movie.get('avgRating', 0))
                    })
            
            watch_history.append({
                **movie_info,
                'watchedAt': item.get('watchedAt', datetime.utcnow()).isoformat()
            })
        
        return jsonify({'userId': user_id, 'watchHistory': watch_history})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/users/<int:user_id>/watch', methods=['POST'])
def add_watch_history(user_id: int):
    """Record that a user watched a movie."""
    try:
        data = request.get_json()
        movie_id = data.get('movieId')
        
        if not movie_id:
            return jsonify({'error': 'movieId is required'}), 400
        
        watch_col = MongoDB.get_collection(Collections.WATCH_HISTORY)
        users_col = MongoDB.get_collection(Collections.USERS)
        
        if watch_col is None:
            return jsonify({
                'message': 'Watch history recorded (mock)',
                'userId': user_id,
                'movieId': movie_id
            })
        
        # Add to watch history
        watch_doc = {
            'userId': user_id,
            'movieId': movie_id,
            'watchedAt': datetime.utcnow()
        }
        watch_col.insert_one(watch_doc)
        
        # Update user's watched movies list
        if users_col is not None:
            users_col.update_one(
                {'userId': user_id},
                {'$addToSet': {'watchedMovies': movie_id}},
                upsert=True
            )
        
        return jsonify({
            'message': 'Watch history recorded',
            'userId': user_id,
            'movieId': movie_id
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/ratings', methods=['POST'])
def add_rating():
    """Add a new rating."""
    try:
        data = request.get_json()
        
        user_id = data.get('userId')
        movie_id = data.get('movieId')
        rating = data.get('rating')
        
        if not all([user_id, movie_id, rating]):
            return jsonify({'error': 'userId, movieId, and rating are required'}), 400
        
        # Validate rating range
        rating = float(rating)
        if rating < 0.5 or rating > 5.0:
            return jsonify({'error': 'Rating must be between 0.5 and 5.0'}), 400
        
        ratings_col = MongoDB.get_collection(Collections.RATINGS)
        users_col = MongoDB.get_collection(Collections.USERS)
        movies_col = MongoDB.get_collection(Collections.MOVIES)
        
        if ratings_col is None:
            return jsonify({
                'message': 'Rating added (mock)',
                'userId': user_id,
                'movieId': movie_id,
                'rating': rating
            }), 201
        
        # Upsert rating
        now = datetime.utcnow()
        ratings_col.update_one(
            {'userId': user_id, 'movieId': movie_id},
            {
                '$set': {
                    'rating': rating,
                    'timestamp': now
                },
                '$setOnInsert': {'createdAt': now}
            },
            upsert=True
        )
        
        # Update user's rated movies
        if users_col is not None:
            users_col.update_one(
                {'userId': user_id},
                {'$addToSet': {'ratedMovies': movie_id}},
                upsert=True
            )
        
        # Update movie's average rating
        if movies_col is not None:
            _update_movie_rating_stats(ratings_col, movies_col, movie_id)
        
        return jsonify({
            'message': 'Rating added successfully',
            'userId': user_id,
            'movieId': movie_id,
            'rating': rating
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/ratings/<int:user_id>/<int:movie_id>', methods=['GET'])
def get_rating(user_id: int, movie_id: int):
    """Get a specific rating."""
    try:
        collection = MongoDB.get_collection(Collections.RATINGS)
        
        if collection is None:
            return jsonify({'userId': user_id, 'movieId': movie_id, 'rating': None})
        
        rating = collection.find_one({'userId': user_id, 'movieId': movie_id})
        
        if rating is None:
            return jsonify({'userId': user_id, 'movieId': movie_id, 'rating': None})
        
        return jsonify({
            'userId': user_id,
            'movieId': movie_id,
            'rating': float(rating['rating']),
            'timestamp': rating.get('timestamp', datetime.utcnow()).isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/ratings/<int:user_id>/<int:movie_id>', methods=['DELETE'])
def delete_rating(user_id: int, movie_id: int):
    """Delete a rating."""
    try:
        ratings_col = MongoDB.get_collection(Collections.RATINGS)
        users_col = MongoDB.get_collection(Collections.USERS)
        movies_col = MongoDB.get_collection(Collections.MOVIES)
        
        if ratings_col is None:
            return jsonify({'message': 'Rating deleted (mock)'})
        
        result = ratings_col.delete_one({'userId': user_id, 'movieId': movie_id})
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Rating not found'}), 404
        
        # Update user's rated movies
        if users_col is not None:
            users_col.update_one(
                {'userId': user_id},
                {'$pull': {'ratedMovies': movie_id}}
            )
        
        # Update movie's average rating
        if movies_col is not None:
            _update_movie_rating_stats(ratings_col, movies_col, movie_id)
        
        return jsonify({'message': 'Rating deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def _update_movie_rating_stats(ratings_col, movies_col, movie_id: int):
    """Update movie's average rating and count."""
    pipeline = [
        {'$match': {'movieId': movie_id}},
        {'$group': {
            '_id': '$movieId',
            'avgRating': {'$avg': '$rating'},
            'ratingCount': {'$sum': 1}
        }}
    ]
    
    result = list(ratings_col.aggregate(pipeline))
    
    if result:
        stats = result[0]
        movies_col.update_one(
            {'movieId': movie_id},
            {'$set': {
                'avgRating': round(stats['avgRating'], 2),
                'ratingCount': stats['ratingCount'],
                'updatedAt': datetime.utcnow()
            }}
        )


def _serialize_user(doc: Dict) -> Dict:
    """Serialize user document."""
    return {
        'userId': doc.get('userId'),
        'username': doc.get('username', f"user_{doc.get('userId')}"),
        'ratedMovies': doc.get('ratedMovies', []),
        'watchedMovies': doc.get('watchedMovies', []),
        'preferences': doc.get('preferences', {})
    }


def _get_mock_users() -> Dict:
    """Return mock users data."""
    users = [
        {'userId': 1, 'username': 'Nguyễn Văn A', 'ratedMovies': [1, 3, 6], 'watchedMovies': [1, 3, 6, 7], 'preferences': {'favoriteGenres': ['Action', 'Sci-Fi']}},
        {'userId': 2, 'username': 'Trần Thị B', 'ratedMovies': [2, 4, 8], 'watchedMovies': [2, 4, 8, 5], 'preferences': {'favoriteGenres': ['Drama', 'Crime']}},
        {'userId': 3, 'username': 'Lê Văn C', 'ratedMovies': [5, 9, 10], 'watchedMovies': [5, 9, 10], 'preferences': {'favoriteGenres': ['Drama', 'Adventure']}},
        {'userId': 4, 'username': 'Phạm Thị D', 'ratedMovies': [1, 2, 3, 4], 'watchedMovies': [1, 2, 3, 4, 5], 'preferences': {'favoriteGenres': ['Drama']}},
        {'userId': 5, 'username': 'Hoàng Văn E', 'ratedMovies': [6, 7, 9], 'watchedMovies': [6, 7, 9, 3], 'preferences': {'favoriteGenres': ['Sci-Fi', 'Action']}},
    ]
    return {'users': users, 'page': 1, 'limit': 20, 'total': len(users)}


def _get_mock_user(user_id: int) -> Dict:
    """Get mock user by ID."""
    users = _get_mock_users()['users']
    for user in users:
        if user['userId'] == user_id:
            return user
    return None


def _get_mock_user_history(user_id: int, limit: int) -> Dict:
    """Get mock user rating history."""
    mock_history = [
        {'movieId': 1, 'title': 'The Shawshank Redemption (1994)', 'genres': ['Drama'], 'userRating': 5.0, 'timestamp': '2024-01-15T10:00:00'},
        {'movieId': 3, 'title': 'The Dark Knight (2008)', 'genres': ['Action', 'Crime', 'Drama'], 'userRating': 4.5, 'timestamp': '2024-01-10T14:30:00'},
        {'movieId': 6, 'title': 'Inception (2010)', 'genres': ['Action', 'Sci-Fi', 'Thriller'], 'userRating': 4.0, 'timestamp': '2024-01-05T20:00:00'},
    ]
    return {'userId': user_id, 'history': mock_history[:limit]}
