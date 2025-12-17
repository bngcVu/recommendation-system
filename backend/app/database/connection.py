"""
MongoDB database connection module.
"""
from pymongo import MongoClient
from pymongo.database import Database
from typing import Optional


class MongoDB:
    """MongoDB connection manager."""
    client: Optional[MongoClient] = None
    db: Optional[Database] = None
    
    @classmethod
    def connect(cls, uri: str, db_name: str) -> None:
        """
        Connect to MongoDB.
        
        Args:
            uri: MongoDB connection URI
            db_name: Database name
        """
        try:
            cls.client = MongoClient(uri)
            cls.db = cls.client[db_name]
            # Test connection
            cls.client.admin.command('ping')
            print(f"✓ Connected to MongoDB database: {db_name}")
        except Exception as e:
            print(f"✗ Failed to connect to MongoDB: {e}")
            # Continue without database for development
            cls.client = None
            cls.db = None
    
    @classmethod
    def get_db(cls) -> Optional[Database]:
        """Get the database instance."""
        return cls.db
    
    @classmethod
    def get_collection(cls, name: str):
        """
        Get a collection from the database.
        
        Args:
            name: Collection name
            
        Returns:
            Collection instance or None
        """
        if cls.db is None:
            return None
        return cls.db[name]
    
    @classmethod
    def close(cls) -> None:
        """Close the MongoDB connection."""
        if cls.client:
            cls.client.close()
            print("MongoDB connection closed")
    
    @classmethod
    def is_connected(cls) -> bool:
        """Check if connected to MongoDB."""
        try:
            if cls.client:
                cls.client.admin.command('ping')
                return True
        except Exception:
            pass
        return False


# Collection names
class Collections:
    """Collection name constants."""
    MOVIES = 'movies'
    USERS = 'users'
    RATINGS = 'ratings'
    MODELS = 'models'
    WATCH_HISTORY = 'watch_history'
