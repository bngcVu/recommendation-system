"""
Routes module exports.
"""
from app.routes.movies import movies_bp
from app.routes.users import users_bp
from app.routes.recommendation import recommendation_bp
from app.routes.analytics import analytics_bp

__all__ = ['movies_bp', 'users_bp', 'recommendation_bp', 'analytics_bp']
