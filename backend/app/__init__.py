"""
Movie Recommendation System Backend
Flask application with MongoDB database
"""
from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.database.connection import MongoDB


def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS for frontend
    CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])
    
    # Initialize MongoDB connection
    MongoDB.connect(app.config['MONGODB_URI'], app.config['MONGODB_DB'])
    
    # Register blueprints
    from app.routes.movies import movies_bp
    from app.routes.users import users_bp
    from app.routes.recommendation import recommendation_bp
    from app.routes.analytics import analytics_bp
    
    app.register_blueprint(movies_bp, url_prefix='/api')
    app.register_blueprint(users_bp, url_prefix='/api')
    app.register_blueprint(recommendation_bp, url_prefix='/api')
    app.register_blueprint(analytics_bp, url_prefix='/api')
    
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'database': 'connected'}
    
    return app
