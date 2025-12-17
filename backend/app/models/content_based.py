"""
Content-Based Filtering recommendation model.
Uses movie genres and TF-IDF vectors to find similar movies.
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Set
from sklearn.metrics.pairwise import cosine_similarity
from scipy import sparse


class ContentBasedModel:
    """Content-Based Filtering using TF-IDF on movie genres."""
    
    def __init__(self):
        """Initialize the content-based model."""
        self.movies_df: Optional[pd.DataFrame] = None
        self.tfidf_matrix: Optional[np.ndarray] = None
        self.similarity_matrix: Optional[np.ndarray] = None
        self.movie_id_to_idx: Dict[int, int] = {}
        self.idx_to_movie_id: Dict[int, int] = {}
        self.embeddings: Optional[np.ndarray] = None
        self.is_fitted: bool = False
    
    def fit(self, movies_df: pd.DataFrame, 
            tfidf_matrix: Optional[np.ndarray] = None,
            embeddings: Optional[np.ndarray] = None,
            use_embeddings: bool = False) -> 'ContentBasedModel':
        """
        Fit the model with movie data.
        
        Args:
            movies_df: Movies dataframe with genres
            tfidf_matrix: Pre-computed TF-IDF matrix (optional)
            embeddings: Pre-computed embeddings (optional)
            use_embeddings: Whether to use embeddings for similarity
            
        Returns:
            Self for chaining
        """
        self.movies_df = movies_df.reset_index(drop=True)
        
        # Create index mappings
        for idx, movie_id in enumerate(movies_df['movieId']):
            self.movie_id_to_idx[movie_id] = idx
            self.idx_to_movie_id[idx] = movie_id
        
        # Compute TF-IDF if not provided
        if tfidf_matrix is None:
            from app.services.vectorization import Vectorizer
            vectorizer = Vectorizer()
            genres_list = movies_df['genres'].tolist()
            tfidf_matrix, _ = vectorizer.tfidf_vectorize(genres_list)
        
        self.tfidf_matrix = tfidf_matrix
        
        # Handle embeddings
        if embeddings is not None:
            self.embeddings = embeddings
        
        # Compute similarity matrix
        if use_embeddings and self.embeddings is not None:
            # Combine TF-IDF and embeddings
            feature_matrix = self._combine_features()
            self.similarity_matrix = cosine_similarity(feature_matrix)
        else:
            # Use only TF-IDF
            if sparse.issparse(self.tfidf_matrix):
                self.similarity_matrix = cosine_similarity(self.tfidf_matrix)
            else:
                self.similarity_matrix = cosine_similarity(self.tfidf_matrix)
        
        self.is_fitted = True
        return self
    
    def _combine_features(self, tfidf_weight: float = 0.5) -> np.ndarray:
        """
        Combine TF-IDF and embedding features.
        
        Args:
            tfidf_weight: Weight for TF-IDF features (1 - weight for embeddings)
            
        Returns:
            Combined feature matrix
        """
        # Normalize TF-IDF
        tfidf = self.tfidf_matrix
        if sparse.issparse(tfidf):
            tfidf = tfidf.toarray()
        tfidf_norm = tfidf / (np.linalg.norm(tfidf, axis=1, keepdims=True) + 1e-8)
        
        # Normalize embeddings
        emb_norm = self.embeddings / (np.linalg.norm(self.embeddings, axis=1, keepdims=True) + 1e-8)
        
        # Weighted combination
        combined = np.hstack([
            tfidf_norm * tfidf_weight,
            emb_norm * (1 - tfidf_weight)
        ])
        
        return combined
    
    def get_similar_movies(self, movie_id: int, 
                           n: int = 10,
                           exclude: Optional[Set[int]] = None) -> List[Dict]:
        """
        Get movies similar to a given movie.
        
        Args:
            movie_id: Movie ID to find similar movies for
            n: Number of similar movies to return
            exclude: Set of movie IDs to exclude
            
        Returns:
            List of similar movies with similarity scores
        """
        if not self.is_fitted:
            raise RuntimeError("Model not fitted. Call fit() first.")
        
        if movie_id not in self.movie_id_to_idx:
            return []
        
        idx = self.movie_id_to_idx[movie_id]
        similarities = self.similarity_matrix[idx]
        
        # Get sorted indices (excluding self)
        similar_indices = np.argsort(similarities)[::-1]
        
        results = []
        exclude = exclude or set()
        
        for sim_idx in similar_indices:
            if len(results) >= n:
                break
            
            sim_movie_id = self.idx_to_movie_id[sim_idx]
            
            if sim_movie_id == movie_id or sim_movie_id in exclude:
                continue
            
            movie_data = self.movies_df.iloc[sim_idx]
            results.append({
                'movieId': int(sim_movie_id),
                'title': movie_data['title'],
                'genres': movie_data['genres'],
                'avgRating': float(movie_data.get('avgRating', 0)),
                'similarity': float(similarities[sim_idx])
            })
        
        return results
    
    def recommend_for_user(self, user_id: int,
                           user_rated_movies: List[Dict],
                           n: int = 10,
                           exclude: Optional[Set[int]] = None) -> List[Dict]:
        """
        Recommend movies for a user based on their rated movies.
        
        Args:
            user_id: User ID
            user_rated_movies: List of {movieId, rating} dicts
            n: Number of recommendations
            exclude: Set of movie IDs to exclude
            
        Returns:
            List of recommended movies
        """
        if not self.is_fitted:
            raise RuntimeError("Model not fitted. Call fit() first.")
        
        if not user_rated_movies:
            # Return popular movies if no history
            return self._get_popular_movies(n, exclude)
        
        # Weight by user ratings
        exclude = exclude or set()
        exclude.update([m['movieId'] for m in user_rated_movies])
        
        # Aggregate similarity scores
        n_movies = len(self.movies_df)
        scores = np.zeros(n_movies)
        weights = np.zeros(n_movies)
        
        for rated in user_rated_movies:
            movie_id = rated['movieId']
            rating = rated.get('rating', 3.0)
            
            if movie_id in self.movie_id_to_idx:
                idx = self.movie_id_to_idx[movie_id]
                # Weight positive ratings more
                weight = (rating - 2.5) / 2.5  # Normalize to [-1, 1]
                scores += self.similarity_matrix[idx] * weight
                weights += np.abs(self.similarity_matrix[idx])
        
        # Normalize scores
        with np.errstate(divide='ignore', invalid='ignore'):
            scores = np.divide(scores, weights, where=weights > 0)
            scores = np.nan_to_num(scores)
        
        # Get top recommendations
        top_indices = np.argsort(scores)[::-1]
        
        results = []
        for idx in top_indices:
            if len(results) >= n:
                break
            
            movie_id = self.idx_to_movie_id[idx]
            if movie_id in exclude:
                continue
            
            movie_data = self.movies_df.iloc[idx]
            results.append({
                'movieId': int(movie_id),
                'title': movie_data['title'],
                'genres': movie_data['genres'],
                'avgRating': float(movie_data.get('avgRating', 0)),
                'score': float(scores[idx]),
                'method': 'content_based'
            })
        
        return results
    
    def predict_rating(self, user_id: int, movie_id: int,
                       user_rated_movies: Optional[List[Dict]] = None) -> Optional[float]:
        """
        Predict rating for a user-movie pair.
        
        Args:
            user_id: User ID
            movie_id: Movie ID
            user_rated_movies: User's rated movies
            
        Returns:
            Predicted rating or None
        """
        if not self.is_fitted or movie_id not in self.movie_id_to_idx:
            return None
        
        if not user_rated_movies:
            return None
        
        movie_idx = self.movie_id_to_idx[movie_id]
        
        weighted_sum = 0.0
        similarity_sum = 0.0
        
        for rated in user_rated_movies:
            rated_id = rated['movieId']
            if rated_id in self.movie_id_to_idx:
                rated_idx = self.movie_id_to_idx[rated_id]
                similarity = self.similarity_matrix[movie_idx, rated_idx]
                
                if similarity > 0:
                    weighted_sum += similarity * rated['rating']
                    similarity_sum += similarity
        
        if similarity_sum > 0:
            return weighted_sum / similarity_sum
        
        return None
    
    def _get_popular_movies(self, n: int, exclude: Optional[Set[int]] = None) -> List[Dict]:
        """Get popular movies as fallback."""
        exclude = exclude or set()
        
        if 'ratingCount' in self.movies_df.columns:
            sorted_df = self.movies_df.sort_values(
                by=['ratingCount', 'avgRating'], 
                ascending=[False, False]
            )
        else:
            sorted_df = self.movies_df.sort_values(
                by='avgRating', ascending=False
            )
        
        results = []
        for _, row in sorted_df.iterrows():
            if row['movieId'] in exclude:
                continue
            
            results.append({
                'movieId': int(row['movieId']),
                'title': row['title'],
                'genres': row['genres'],
                'avgRating': float(row.get('avgRating', 0)),
                'score': float(row.get('avgRating', 0)),
                'method': 'popular'
            })
            
            if len(results) >= n:
                break
        
        return results
