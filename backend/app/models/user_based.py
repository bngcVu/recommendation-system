"""
User-Based Collaborative Filtering recommendation model.
Finds similar users to make recommendations.
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Set
from scipy import sparse
from sklearn.metrics.pairwise import cosine_similarity


class UserBasedModel:
    """User-Based Collaborative Filtering using user similarity."""
    
    def __init__(self, k: int = 20, min_common: int = 3):
        """
        Initialize the user-based model.
        
        Args:
            k: Number of similar users to consider
            min_common: Minimum common rated items for similarity
        """
        self.k = k
        self.min_common = min_common
        self.ratings_df: Optional[pd.DataFrame] = None
        self.movies_df: Optional[pd.DataFrame] = None
        self.user_similarity: Optional[np.ndarray] = None
        self.user_item_matrix: Optional[np.ndarray] = None
        self.user_means: Optional[np.ndarray] = None
        self.user_ids: List[int] = []
        self.movie_ids: List[int] = []
        self.user_to_idx: Dict[int, int] = {}
        self.idx_to_user: Dict[int, int] = {}
        self.movie_to_idx: Dict[int, int] = {}
        self.idx_to_movie: Dict[int, int] = {}
        self.is_fitted: bool = False
    
    def fit(self, ratings_df: pd.DataFrame,
            movies_df: Optional[pd.DataFrame] = None) -> 'UserBasedModel':
        """
        Fit the model with ratings data.
        
        Args:
            ratings_df: Ratings dataframe
            movies_df: Movies dataframe for movie info
            
        Returns:
            Self for chaining
        """
        self.ratings_df = ratings_df
        self.movies_df = movies_df
        
        # Create user-item matrix
        self.user_ids = sorted(ratings_df['userId'].unique())
        self.movie_ids = sorted(ratings_df['movieId'].unique())
        
        for idx, uid in enumerate(self.user_ids):
            self.user_to_idx[uid] = idx
            self.idx_to_user[idx] = uid
        
        for idx, mid in enumerate(self.movie_ids):
            self.movie_to_idx[mid] = idx
            self.idx_to_movie[idx] = mid
        
        # Build sparse matrix
        n_users = len(self.user_ids)
        n_items = len(self.movie_ids)
        
        rows = ratings_df['userId'].map(self.user_to_idx).values
        cols = ratings_df['movieId'].map(self.movie_to_idx).values
        data = ratings_df['rating'].values
        
        self.user_item_matrix = sparse.csr_matrix(
            (data, (rows, cols)), shape=(n_users, n_items)
        ).toarray()
        
        # Compute user means
        self._compute_user_means()
        
        # Compute user-user similarity
        self._compute_user_similarity()
        
        self.is_fitted = True
        return self
    
    def _compute_user_means(self) -> None:
        """Compute mean rating for each user."""
        mask = self.user_item_matrix > 0
        sums = np.sum(self.user_item_matrix, axis=1)
        counts = np.sum(mask, axis=1)
        
        self.user_means = np.divide(
            sums, counts, 
            out=np.full_like(sums, 3.0, dtype=float),
            where=counts > 0
        )
    
    def _compute_user_similarity(self) -> None:
        """Compute user-user similarity using Pearson correlation."""
        n_users = len(self.user_ids)
        self.user_similarity = np.zeros((n_users, n_users))
        
        # Mean-center ratings
        centered = self.user_item_matrix - self.user_means[:, np.newaxis]
        centered = np.where(self.user_item_matrix > 0, centered, 0)
        
        # Compute cosine similarity on centered matrix
        norms = np.linalg.norm(centered, axis=1, keepdims=True)
        norms = np.where(norms > 0, norms, 1)
        normalized = centered / norms
        
        self.user_similarity = normalized @ normalized.T
        
        # Zero out diagonal
        np.fill_diagonal(self.user_similarity, 0)
    
    def get_similar_users(self, user_id: int, n: int = 10) -> List[Dict]:
        """
        Get users similar to a given user.
        
        Args:
            user_id: User ID
            n: Number of similar users
            
        Returns:
            List of similar users with scores
        """
        if not self.is_fitted or user_id not in self.user_to_idx:
            return []
        
        user_idx = self.user_to_idx[user_id]
        similarities = self.user_similarity[user_idx]
        
        # Get top-n similar users
        similar_indices = np.argsort(similarities)[::-1][:n]
        
        results = []
        for sim_idx in similar_indices:
            sim_user_id = self.idx_to_user[sim_idx]
            results.append({
                'userId': int(sim_user_id),
                'similarity': float(similarities[sim_idx])
            })
        
        return results
    
    def predict_rating(self, user_id: int, movie_id: int) -> Optional[float]:
        """
        Predict rating for a user-movie pair.
        
        Args:
            user_id: User ID
            movie_id: Movie ID
            
        Returns:
            Predicted rating or None
        """
        if not self.is_fitted:
            return None
        
        if user_id not in self.user_to_idx or movie_id not in self.movie_to_idx:
            return None
        
        user_idx = self.user_to_idx[user_id]
        movie_idx = self.movie_to_idx[movie_id]
        
        # Get users who rated this movie
        rated_mask = self.user_item_matrix[:, movie_idx] > 0
        rated_indices = np.where(rated_mask)[0]
        
        if len(rated_indices) == 0:
            return self.user_means[user_idx]
        
        # Get similarities
        similarities = self.user_similarity[user_idx, rated_indices]
        
        # Use top-k similar users
        if len(rated_indices) > self.k:
            top_k_pos = np.argsort(similarities)[::-1][:self.k]
            similarities = similarities[top_k_pos]
            rated_indices = rated_indices[top_k_pos]
        
        # Filter positive similarities
        pos_mask = similarities > 0
        if not np.any(pos_mask):
            return self.user_means[user_idx]
        
        weights = similarities[pos_mask]
        neighbor_indices = rated_indices[pos_mask]
        
        # Compute weighted average of deviations from means
        ratings = self.user_item_matrix[neighbor_indices, movie_idx]
        neighbor_means = self.user_means[neighbor_indices]
        deviations = ratings - neighbor_means
        
        predicted = self.user_means[user_idx] + np.sum(weights * deviations) / np.sum(weights)
        
        return float(np.clip(predicted, 0.5, 5.0))
    
    def recommend(self, user_id: int, n: int = 10,
                  exclude: Optional[Set[int]] = None) -> List[Dict]:
        """
        Recommend movies for a user.
        
        Args:
            user_id: User ID
            n: Number of recommendations
            exclude: Movie IDs to exclude
            
        Returns:
            List of recommended movies
        """
        if not self.is_fitted:
            return []
        
        exclude = exclude or set()
        
        if user_id not in self.user_to_idx:
            return self._get_popular_items(n, exclude)
        
        user_idx = self.user_to_idx[user_id]
        user_ratings = self.user_item_matrix[user_idx]
        
        # Add rated movies to exclude
        rated_indices = np.where(user_ratings > 0)[0]
        rated_movie_ids = {self.idx_to_movie[idx] for idx in rated_indices}
        exclude = exclude.union(rated_movie_ids)
        
        # Get similar users
        similar_indices = np.argsort(self.user_similarity[user_idx])[::-1][:self.k]
        similarities = self.user_similarity[user_idx, similar_indices]
        
        # Filter positive similarities
        pos_mask = similarities > 0
        if not np.any(pos_mask):
            return self._get_popular_items(n, exclude)
        
        similar_indices = similar_indices[pos_mask]
        similarities = similarities[pos_mask]
        
        # Predict ratings for unrated movies
        predictions = []
        for movie_idx in range(len(self.movie_ids)):
            movie_id = self.idx_to_movie[movie_idx]
            
            if movie_id in exclude:
                continue
            
            # Check if any similar user rated this movie
            neighbor_ratings = self.user_item_matrix[similar_indices, movie_idx]
            rated_mask = neighbor_ratings > 0
            
            if not np.any(rated_mask):
                continue
            
            # Weighted prediction
            weights = similarities[rated_mask]
            ratings = neighbor_ratings[rated_mask]
            neighbor_means = self.user_means[similar_indices[rated_mask]]
            deviations = ratings - neighbor_means
            
            pred = self.user_means[user_idx] + np.sum(weights * deviations) / np.sum(weights)
            pred = float(np.clip(pred, 0.5, 5.0))
            
            predictions.append((movie_id, pred))
        
        # Sort by predicted rating
        predictions.sort(key=lambda x: x[1], reverse=True)
        
        # Return top-n
        results = []
        for movie_id, score in predictions[:n]:
            movie_info = self._get_movie_info(movie_id)
            movie_info['score'] = float(score)
            movie_info['method'] = 'user_based'
            results.append(movie_info)
        
        return results
    
    def _get_movie_info(self, movie_id: int) -> Dict:
        """Get movie information."""
        info = {
            'movieId': int(movie_id),
            'title': f'Movie {movie_id}',
            'genres': [],
            'avgRating': 0.0
        }
        
        if self.movies_df is not None:
            movie_row = self.movies_df[self.movies_df['movieId'] == movie_id]
            if not movie_row.empty:
                row = movie_row.iloc[0]
                info['title'] = row.get('title', info['title'])
                info['genres'] = row.get('genres', [])
                info['avgRating'] = float(row.get('avgRating', 0))
        
        return info
    
    def _get_popular_items(self, n: int, exclude: Set[int]) -> List[Dict]:
        """Get popular items for cold start."""
        if self.movies_df is not None:
            sorted_df = self.movies_df.sort_values(
                by='avgRating', ascending=False
            )
            
            results = []
            for _, row in sorted_df.iterrows():
                if row['movieId'] in exclude:
                    continue
                if row['movieId'] not in self.movie_to_idx:
                    continue
                
                results.append({
                    'movieId': int(row['movieId']),
                    'title': row['title'],
                    'genres': row.get('genres', []),
                    'avgRating': float(row.get('avgRating', 0)),
                    'score': float(row.get('avgRating', 0)),
                    'method': 'popular'
                })
                
                if len(results) >= n:
                    break
            
            return results
        
        return []
