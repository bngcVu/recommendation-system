"""
MongoDB helper utilities for Jupyter notebooks.
"""
from pymongo import MongoClient
from pymongo.database import Database
from datetime import datetime
from typing import Dict, List, Optional, Any
import pickle


class MongoHelper:
    """Helper class for MongoDB operations in notebooks."""
    
    def __init__(self, uri: str = 'mongodb://localhost:27017', 
                 db_name: str = 'movie_recommendation'):
        """
        Initialize MongoDB connection.
        
        Args:
            uri: MongoDB connection URI
            db_name: Database name
        """
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        print(f"Connected to MongoDB: {db_name}")
    
    def save_model_metrics(self, model_name: str, metrics: Dict, 
                           version: str = '1.0', 
                           parameters: Optional[Dict] = None) -> None:
        """
        Save model metrics to MongoDB.
        
        Args:
            model_name: Name of the model
            metrics: Dict of metrics (rmse, mae, precision, recall, etc.)
            version: Model version
            parameters: Model hyperparameters
        """
        doc = {
            'modelName': model_name,
            'version': version,
            'metrics': metrics,
            'parameters': parameters or {},
            'trainedAt': datetime.utcnow(),
            'isActive': True
        }
        
        self.db.models.update_one(
            {'modelName': model_name, 'version': version},
            {'$set': doc},
            upsert=True
        )
        print(f"✓ Saved metrics for {model_name} v{version}")
    
    def get_model_metrics(self, model_name: str, 
                          version: Optional[str] = None) -> Optional[Dict]:
        """
        Get model metrics from MongoDB.
        
        Args:
            model_name: Name of the model
            version: Specific version (optional)
            
        Returns:
            Metrics dict or None
        """
        query = {'modelName': model_name}
        if version:
            query['version'] = version
        
        doc = self.db.models.find_one(query, sort=[('trainedAt', -1)])
        return doc
    
    def save_similarity_matrix(self, model_name: str, 
                                matrix: Any,
                                version: str = '1.0') -> None:
        """
        Save similarity matrix to MongoDB (pickled).
        
        Args:
            model_name: Name of the model
            matrix: Numpy array or sparse matrix
            version: Model version
        """
        pickled = pickle.dumps(matrix)
        
        self.db.similarity_matrices.update_one(
            {'modelName': model_name, 'version': version},
            {
                '$set': {
                    'modelName': model_name,
                    'version': version,
                    'matrix': pickled,
                    'updatedAt': datetime.utcnow()
                }
            },
            upsert=True
        )
        print(f"✓ Saved similarity matrix for {model_name}")
    
    def load_similarity_matrix(self, model_name: str,
                                version: str = '1.0') -> Optional[Any]:
        """
        Load similarity matrix from MongoDB.
        
        Args:
            model_name: Name of the model
            version: Model version
            
        Returns:
            Unpickled matrix or None
        """
        doc = self.db.similarity_matrices.find_one({
            'modelName': model_name,
            'version': version
        })
        
        if doc and 'matrix' in doc:
            return pickle.loads(doc['matrix'])
        return None
    
    def insert_movies(self, movies_data: List[Dict]) -> int:
        """
        Insert movies into database.
        
        Args:
            movies_data: List of movie dictionaries
            
        Returns:
            Number of inserted documents
        """
        if not movies_data:
            return 0
        
        result = self.db.movies.insert_many(movies_data)
        print(f"✓ Inserted {len(result.inserted_ids)} movies")
        return len(result.inserted_ids)
    
    def insert_ratings(self, ratings_data: List[Dict]) -> int:
        """
        Insert ratings into database.
        
        Args:
            ratings_data: List of rating dictionaries
            
        Returns:
            Number of inserted documents
        """
        if not ratings_data:
            return 0
        
        result = self.db.ratings.insert_many(ratings_data)
        print(f"✓ Inserted {len(result.inserted_ids)} ratings")
        return len(result.inserted_ids)
    
    def insert_users(self, users_data: List[Dict]) -> int:
        """
        Insert users into database.
        
        Args:
            users_data: List of user dictionaries
            
        Returns:
            Number of inserted documents
        """
        if not users_data:
            return 0
        
        result = self.db.users.insert_many(users_data)
        print(f"✓ Inserted {len(result.inserted_ids)} users")
        return len(result.inserted_ids)
    
    def clear_collection(self, collection_name: str) -> int:
        """
        Clear all documents from a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Number of deleted documents
        """
        result = self.db[collection_name].delete_many({})
        print(f"✓ Deleted {result.deleted_count} documents from {collection_name}")
        return result.deleted_count
    
    def get_stats(self) -> Dict:
        """
        Get database statistics.
        
        Returns:
            Dict with collection counts
        """
        return {
            'movies': self.db.movies.count_documents({}),
            'users': self.db.users.count_documents({}),
            'ratings': self.db.ratings.count_documents({}),
            'models': self.db.models.count_documents({})
        }
    
    def close(self) -> None:
        """Close MongoDB connection."""
        self.client.close()
        print("MongoDB connection closed")
