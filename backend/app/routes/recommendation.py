"""
API routes for movie recommendations.
"""
from flask import Blueprint, request, jsonify
from app.database.connection import MongoDB, Collections
from typing import Dict, List
import pickle
import os

recommendation_bp = Blueprint('recommendation', __name__)
_model_cache: Dict = {}


def _get_model(model_name: str):
    """Get or load a recommendation model."""
    if model_name in _model_cache:
        return _model_cache[model_name]
    
    from app.config import Config
    model_path = os.path.join(Config.MODELS_DIR, f'{model_name}.pkl')
    
    if os.path.exists(model_path):
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
            _model_cache[model_name] = model
            return model
    return None


def _get_user_ratings(user_id: int) -> List[Dict]:
    """Get user's ratings from database."""
    collection = MongoDB.get_collection(Collections.RATINGS)
    if collection is None:
        return _get_mock_user_ratings(user_id)
    
    cursor = collection.find({'userId': user_id})
    return [{'movieId': doc['movieId'], 'rating': float(doc['rating'])} for doc in cursor]


@recommendation_bp.route('/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id: int):
    """Get movie recommendations for a user."""
    try:
        model_name = request.args.get('model', 'hybrid')
        n = min(int(request.args.get('n', 10)), 50)
        
        valid_models = ['content_based', 'item_based', 'user_based', 'hybrid']
        if model_name not in valid_models:
            return jsonify({'error': f'Invalid model. Choose from: {valid_models}'}), 400
        
        user_ratings = _get_user_ratings(user_id)
        exclude_ids = {r['movieId'] for r in user_ratings}
        
        model = _get_model(model_name)
        
        if model is not None:
            if model_name == 'content_based':
                recommendations = model.recommend_for_user(user_id, user_ratings, n=n, exclude=exclude_ids)
            elif model_name == 'hybrid':
                recommendations = model.recommend(user_id, n=n, exclude=exclude_ids, user_rated_movies=user_ratings)
            else:
                recommendations = model.recommend(user_id, n=n, exclude=exclude_ids)
        else:
            recommendations = _get_mock_recommendations(user_id, model_name, n, exclude_ids)
        
        return jsonify({'userId': user_id, 'model': model_name, 'recommendations': recommendations})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@recommendation_bp.route('/similar/<int:movie_id>', methods=['GET'])
def get_similar_movies(movie_id: int):
    """Get movies similar to a given movie."""
    try:
        model_name = request.args.get('model', 'hybrid')
        n = min(int(request.args.get('n', 10)), 50)
        
        model = _get_model(model_name)
        
        if model is not None:
            if model_name == 'content_based':
                similar = model.get_similar_movies(movie_id, n=n)
            elif model_name == 'item_based':
                similar = model.get_similar_items(movie_id, n=n)
            elif model_name == 'hybrid':
                similar = model.get_similar_movies(movie_id, n=n)
            else:
                similar = []
        else:
            similar = _get_mock_similar_movies(movie_id, n)
        
        return jsonify({'movieId': movie_id, 'model': model_name, 'similar': similar})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@recommendation_bp.route('/models', methods=['GET'])
def get_models():
    """Get available recommendation models and their metrics."""
    try:
        collection = MongoDB.get_collection(Collections.MODELS)
        
        if collection is None:
            return jsonify({'models': _get_mock_model_metrics()})
        
        cursor = collection.find({'isActive': True})
        models = []
        for doc in cursor:
            models.append({
                'modelName': doc.get('modelName'),
                'version': doc.get('version', '1.0'),
                'metrics': doc.get('metrics', {}),
                'trainedAt': doc.get('trainedAt', '').isoformat() if doc.get('trainedAt') else None,
                'isActive': doc.get('isActive', True)
            })
        
        return jsonify({'models': models})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@recommendation_bp.route('/models/compare', methods=['GET'])
def compare_models():
    """Compare metrics across all models."""
    try:
        collection = MongoDB.get_collection(Collections.MODELS)
        
        if collection is None:
            return jsonify({'comparison': {'metrics': ['rmse', 'mae', 'precision@10', 'recall@10'], 'models': _get_mock_model_metrics()}})
        
        cursor = collection.find({'isActive': True})
        comparison = {'metrics': ['rmse', 'mae', 'precision@10', 'recall@10'], 'models': []}
        
        for doc in cursor:
            comparison['models'].append({'modelName': doc.get('modelName'), 'metrics': doc.get('metrics', {})})
        
        return jsonify(comparison)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def _get_mock_user_ratings(user_id: int) -> List[Dict]:
    mock_ratings = {
        1: [{'movieId': 1, 'rating': 5.0}, {'movieId': 3, 'rating': 4.5}],
        2: [{'movieId': 2, 'rating': 5.0}, {'movieId': 4, 'rating': 4.0}],
    }
    return mock_ratings.get(user_id, [])


def _get_mock_recommendations(user_id: int, model_name: str, n: int, exclude: set) -> List[Dict]:
    mock_movies = [
        {'movieId': 11, 'title': 'The Lord of the Rings (2001)', 'genres': ['Adventure', 'Fantasy'], 'avgRating': 4.6, 'score': 4.8, 'method': model_name},
        {'movieId': 12, 'title': 'Star Wars (1977)', 'genres': ['Action', 'Adventure'], 'avgRating': 4.4, 'score': 4.6, 'method': model_name},
        {'movieId': 7, 'title': 'The Matrix (1999)', 'genres': ['Action', 'Sci-Fi'], 'avgRating': 4.4, 'score': 4.5, 'method': model_name},
        {'movieId': 9, 'title': 'Interstellar (2014)', 'genres': ['Drama', 'Sci-Fi'], 'avgRating': 4.3, 'score': 4.4, 'method': model_name},
        {'movieId': 5, 'title': 'Forrest Gump (1994)', 'genres': ['Drama', 'Romance'], 'avgRating': 4.5, 'score': 4.3, 'method': model_name},
    ]
    return [m for m in mock_movies if m['movieId'] not in exclude][:n]


def _get_mock_similar_movies(movie_id: int, n: int) -> List[Dict]:
    return [
        {'movieId': 2, 'title': 'The Godfather (1972)', 'genres': ['Crime', 'Drama'], 'avgRating': 4.7, 'similarity': 0.85},
        {'movieId': 4, 'title': 'Pulp Fiction (1994)', 'genres': ['Crime', 'Drama'], 'avgRating': 4.5, 'similarity': 0.80},
        {'movieId': 5, 'title': 'Forrest Gump (1994)', 'genres': ['Drama'], 'avgRating': 4.5, 'similarity': 0.78},
    ][:n]


def _get_mock_model_metrics() -> List[Dict]:
    return [
        {'modelName': 'content_based', 'version': '1.0', 'metrics': {'rmse': 0.92, 'mae': 0.71, 'precision@10': 0.35, 'recall@10': 0.28}},
        {'modelName': 'item_based', 'version': '1.0', 'metrics': {'rmse': 0.88, 'mae': 0.68, 'precision@10': 0.38, 'recall@10': 0.31}},
        {'modelName': 'user_based', 'version': '1.0', 'metrics': {'rmse': 0.90, 'mae': 0.70, 'precision@10': 0.36, 'recall@10': 0.29}},
        {'modelName': 'hybrid', 'version': '1.0', 'metrics': {'rmse': 0.85, 'mae': 0.65, 'precision@10': 0.42, 'recall@10': 0.35}},
    ]
