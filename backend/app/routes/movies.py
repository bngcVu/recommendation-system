"""
API routes for movie management.
"""
from flask import Blueprint, request, jsonify
from app.database.connection import MongoDB, Collections
from typing import List, Dict, Any


movies_bp = Blueprint('movies', __name__)


@movies_bp.route('/movies', methods=['GET'])
def get_movies():
    """
    Get list of movies with pagination and filtering.
    
    Query params:
        page: Page number (default 1)
        limit: Items per page (default 20)
        genre: Filter by genre
        sort: Sort field (avgRating, ratingCount, title)
        order: Sort order (asc, desc)
        search: Search by title
    """
    try:
        # Get query parameters
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 20)), 100)
        genre = request.args.get('genre')
        sort_field = request.args.get('sort', 'avgRating')
        sort_order = request.args.get('order', 'desc')
        search = request.args.get('search')
        
        # Build query
        query = {}
        
        if genre:
            query['genres'] = genre
        
        if search:
            query['$text'] = {'$search': search}
        
        # Get collection
        collection = MongoDB.get_collection(Collections.MOVIES)
        
        if collection is None:
            # Return mock data if no database
            return jsonify(_get_mock_movies(page, limit))
        
        # Sort direction
        sort_dir = -1 if sort_order == 'desc' else 1
        
        # Execute query
        skip = (page - 1) * limit
        cursor = collection.find(query).sort(sort_field, sort_dir).skip(skip).limit(limit)
        
        movies = []
        for doc in cursor:
            movies.append(_serialize_movie(doc))
        
        # Get total count
        total = collection.count_documents(query)
        
        return jsonify({
            'movies': movies,
            'page': page,
            'limit': limit,
            'total': total,
            'pages': (total + limit - 1) // limit
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@movies_bp.route('/movies/<int:movie_id>', methods=['GET'])
def get_movie(movie_id: int):
    """Get a single movie by ID."""
    try:
        collection = MongoDB.get_collection(Collections.MOVIES)
        
        if collection is None:
            # Return mock data
            mock = _get_mock_movie(movie_id)
            if mock:
                return jsonify(mock)
            return jsonify({'error': 'Movie not found'}), 404
        
        movie = collection.find_one({'movieId': movie_id})
        
        if movie is None:
            return jsonify({'error': 'Movie not found'}), 404
        
        return jsonify(_serialize_movie(movie))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@movies_bp.route('/movies/genre/<genre>', methods=['GET'])
def get_movies_by_genre(genre: str):
    """Get movies by genre."""
    try:
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 20)), 100)
        
        collection = MongoDB.get_collection(Collections.MOVIES)
        
        if collection is None:
            return jsonify(_get_mock_movies_by_genre(genre, page, limit))
        
        skip = (page - 1) * limit
        
        cursor = collection.find({'genres': genre}).sort('avgRating', -1).skip(skip).limit(limit)
        movies = [_serialize_movie(doc) for doc in cursor]
        
        total = collection.count_documents({'genres': genre})
        
        return jsonify({
            'movies': movies,
            'genre': genre,
            'page': page,
            'limit': limit,
            'total': total
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@movies_bp.route('/movies/top', methods=['GET'])
def get_top_movies():
    """Get top rated movies."""
    try:
        limit = min(int(request.args.get('limit', 10)), 50)
        min_ratings = int(request.args.get('min_ratings', 100))
        
        collection = MongoDB.get_collection(Collections.MOVIES)
        
        if collection is None:
            return jsonify({'movies': _get_mock_top_movies(limit)})
        
        cursor = collection.find(
            {'ratingCount': {'$gte': min_ratings}}
        ).sort('avgRating', -1).limit(limit)
        
        movies = [_serialize_movie(doc) for doc in cursor]
        
        return jsonify({'movies': movies})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@movies_bp.route('/movies/search', methods=['GET'])
def search_movies():
    """Search movies by title."""
    try:
        query = request.args.get('q', '')
        limit = min(int(request.args.get('limit', 20)), 50)
        
        if not query:
            return jsonify({'movies': [], 'query': query})
        
        collection = MongoDB.get_collection(Collections.MOVIES)
        
        if collection is None:
            # Mock search
            return jsonify({
                'movies': _mock_search_movies(query, limit),
                'query': query
            })
        
        # Text search
        cursor = collection.find(
            {'$text': {'$search': query}},
            {'score': {'$meta': 'textScore'}}
        ).sort([('score', {'$meta': 'textScore'})]).limit(limit)
        
        movies = [_serialize_movie(doc) for doc in cursor]
        
        return jsonify({'movies': movies, 'query': query})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@movies_bp.route('/genres', methods=['GET'])
def get_genres():
    """Get all available genres."""
    try:
        collection = MongoDB.get_collection(Collections.MOVIES)
        
        if collection is None:
            return jsonify({'genres': _get_all_genres()})
        
        # Aggregate distinct genres
        genres = collection.distinct('genres')
        
        # Filter out None values and sort
        genres = [g for g in genres if g is not None and isinstance(g, str)]
        
        return jsonify({'genres': sorted(genres)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def _serialize_movie(doc: Dict) -> Dict:
    """Serialize MongoDB document to JSON-safe dict."""
    year = doc.get('year')
    # Ensure year is a valid number or None
    if year is not None:
        try:
            year = int(year)
        except (ValueError, TypeError):
            year = None
    
    return {
        'movieId': doc.get('movieId'),
        'title': doc.get('title', ''),
        'genres': doc.get('genres', []),
        'year': year,
        'avgRating': float(doc.get('avgRating', 0) or 0),
        'ratingCount': int(doc.get('ratingCount', 0) or 0)
    }


# Mock data functions for development without database
def _get_mock_movies(page: int, limit: int) -> Dict:
    """Return mock movies data."""
    mock_movies = [
        {'movieId': 1, 'title': 'The Shawshank Redemption (1994)', 'genres': ['Drama'], 'year': 1994, 'avgRating': 4.8, 'ratingCount': 12453},
        {'movieId': 2, 'title': 'The Godfather (1972)', 'genres': ['Crime', 'Drama'], 'year': 1972, 'avgRating': 4.7, 'ratingCount': 9821},
        {'movieId': 3, 'title': 'The Dark Knight (2008)', 'genres': ['Action', 'Crime', 'Drama'], 'year': 2008, 'avgRating': 4.6, 'ratingCount': 15234},
        {'movieId': 4, 'title': 'Pulp Fiction (1994)', 'genres': ['Crime', 'Drama'], 'year': 1994, 'avgRating': 4.5, 'ratingCount': 8932},
        {'movieId': 5, 'title': 'Forrest Gump (1994)', 'genres': ['Drama', 'Romance'], 'year': 1994, 'avgRating': 4.5, 'ratingCount': 11234},
        {'movieId': 6, 'title': 'Inception (2010)', 'genres': ['Action', 'Sci-Fi', 'Thriller'], 'year': 2010, 'avgRating': 4.4, 'ratingCount': 13456},
        {'movieId': 7, 'title': 'The Matrix (1999)', 'genres': ['Action', 'Sci-Fi'], 'year': 1999, 'avgRating': 4.4, 'ratingCount': 10234},
        {'movieId': 8, 'title': 'Goodfellas (1990)', 'genres': ['Biography', 'Crime', 'Drama'], 'year': 1990, 'avgRating': 4.3, 'ratingCount': 7654},
        {'movieId': 9, 'title': 'Interstellar (2014)', 'genres': ['Adventure', 'Drama', 'Sci-Fi'], 'year': 2014, 'avgRating': 4.3, 'ratingCount': 12876},
        {'movieId': 10, 'title': 'Fight Club (1999)', 'genres': ['Drama'], 'year': 1999, 'avgRating': 4.3, 'ratingCount': 9876},
    ]
    
    start = (page - 1) * limit
    end = start + limit
    
    return {
        'movies': mock_movies[start:end],
        'page': page,
        'limit': limit,
        'total': len(mock_movies),
        'pages': 1
    }


def _get_mock_movie(movie_id: int) -> Dict:
    """Get mock movie by ID."""
    movies = _get_mock_movies(1, 20)['movies']
    for movie in movies:
        if movie['movieId'] == movie_id:
            return movie
    return None


def _get_mock_movies_by_genre(genre: str, page: int, limit: int) -> Dict:
    """Get mock movies filtered by genre."""
    all_movies = _get_mock_movies(1, 100)['movies']
    filtered = [m for m in all_movies if genre in m.get('genres', [])]
    
    start = (page - 1) * limit
    end = start + limit
    
    return {
        'movies': filtered[start:end],
        'genre': genre,
        'page': page,
        'limit': limit,
        'total': len(filtered)
    }


def _get_mock_top_movies(limit: int) -> List[Dict]:
    """Get mock top movies."""
    return _get_mock_movies(1, limit)['movies']


def _mock_search_movies(query: str, limit: int) -> List[Dict]:
    """Mock movie search."""
    all_movies = _get_mock_movies(1, 100)['movies']
    query_lower = query.lower()
    return [m for m in all_movies if query_lower in m['title'].lower()][:limit]


def _get_all_genres() -> List[str]:
    """Get all available genres."""
    return [
        'Action', 'Adventure', 'Animation', 'Biography', 'Comedy',
        'Crime', 'Documentary', 'Drama', 'Family', 'Fantasy',
        'Horror', 'Musical', 'Mystery', 'Romance', 'Sci-Fi',
        'Thriller', 'War', 'Western'
    ]
