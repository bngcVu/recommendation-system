"""
MongoDB collection schemas and indices.
"""
from datetime import datetime
from typing import TypedDict, List, Optional


class MovieSchema(TypedDict):
    """Movie document schema."""
    movieId: int
    title: str
    genres: List[str]
    year: Optional[int]
    avgRating: float
    ratingCount: int
    tfidfVector: Optional[List[float]]
    embedding: Optional[List[float]]
    createdAt: datetime
    updatedAt: datetime


class UserSchema(TypedDict):
    """User document schema."""
    userId: int
    username: str
    ratedMovies: List[int]
    watchedMovies: List[int]
    preferences: dict
    createdAt: datetime
    updatedAt: datetime


class RatingSchema(TypedDict):
    """Rating document schema."""
    userId: int
    movieId: int
    rating: float
    timestamp: datetime
    createdAt: datetime


class ModelSchema(TypedDict):
    """Model document schema for storing model metrics."""
    modelName: str
    version: str
    metrics: dict
    parameters: dict
    trainedAt: datetime
    isActive: bool


class WatchHistorySchema(TypedDict):
    """Watch history document schema."""
    userId: int
    movieId: int
    watchedAt: datetime
    watchDuration: Optional[int]


def create_indices(db):
    """
    Create database indices for optimal query performance.
    
    Args:
        db: MongoDB database instance
    """
    # Movies indices
    db.movies.create_index("movieId", unique=True)
    db.movies.create_index("genres")
    db.movies.create_index([("avgRating", -1)])
    db.movies.create_index([("title", "text")])
    
    # Users indices
    db.users.create_index("userId", unique=True)
    db.users.create_index("username", unique=True)
    
    # Ratings indices
    db.ratings.create_index([("userId", 1), ("movieId", 1)], unique=True)
    db.ratings.create_index("movieId")
    db.ratings.create_index([("timestamp", -1)])
    
    # Models indices
    db.models.create_index([("modelName", 1), ("version", 1)], unique=True)
    
    # Watch history indices
    db.watch_history.create_index([("userId", 1), ("movieId", 1)])
    db.watch_history.create_index([("watchedAt", -1)])
    
    print("✓ Database indices created successfully")
