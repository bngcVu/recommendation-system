"""
Application configuration settings.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # MongoDB Configuration
    MONGODB_HOST = os.environ.get('MONGODB_HOST', 'localhost')
    MONGODB_PORT = int(os.environ.get('MONGODB_PORT', 27017))
    MONGODB_USER = os.environ.get('MONGODB_USER', '')
    MONGODB_PASSWORD = os.environ.get('MONGODB_PASSWORD', '')
    MONGODB_DB = os.environ.get('MONGODB_DB', 'movie_recommendation')
    
    # Build MongoDB URI
    if MONGODB_USER and MONGODB_PASSWORD:
        MONGODB_URI = f"mongodb://{MONGODB_USER}:{MONGODB_PASSWORD}@{MONGODB_HOST}:{MONGODB_PORT}"
    else:
        MONGODB_URI = f"mongodb://{MONGODB_HOST}:{MONGODB_PORT}"
    
    # Model paths
    MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models_saved')
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    
    # Recommendation settings
    DEFAULT_N_RECOMMENDATIONS = 10
    SIMILARITY_THRESHOLD = 0.1


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    MONGODB_DB = 'movie_recommendation_test'
