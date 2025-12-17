"""
Item-Based Collaborative Filtering recommendation model.
Finds similar items based on user rating patterns.
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Set, Tuple
from scipy import sparse
from sklearn.metrics.pairwise import cosine_similarity


class ItemBasedModel:
    """Item-Based Collaborative Filtering using rating patterns."""
    
    def __init__(self, k: int = 20, min_ratings: int = 5):
        """
        Initialize the item-based model.
        
        Args:
            k: Number of similar items to consider
            min_ratings: Minimum ratings required for an item
        """
        self.k = k
        self.min_ratings = min_ratings
        self.ratings_df: Optional[pd.DataFrame] = None
        self.movies_df: Optional[pd.DataFrame] = None
        self.item_similarity: Optional[np.ndarray] = None
        self.user_item_matrix: Optional[np.ndarray] = None
        self.user_ids: List[int] = []
        self.movie_ids: List[int] = []
        self.movie_to_idx: Dict[int, int] = {}
        self.idx_to_movie: Dict[int, int] = {}
        self.user_to_idx: Dict[int, int] = {}
        self.idx_to_user: Dict[int, int] = {}
        self.is_fitted: bool = False
    
    def fit(self, ratings_df: pd.DataFrame,
            movies_df: Optional[pd.DataFrame] = None) -> 'ItemBasedModel':
        """
        Fit the model with ratings data.
        
        Args:
            ratings_df: Ratings dataframe with userId, movieId, rating
            movies_df: Movies dataframe for movie info
            
        Returns:
            Self for chaining
        """
        self.ratings_df = ratings_df
        self.movies_df = movies_df
        
        # Filter items with minimum ratings
        item_counts = ratings_df.groupby('movieId').size()
        valid_items = item_counts[item_counts >= self.min_ratings].index
        filtered_df = ratings_df[ratings_df['movieId'].isin(valid_items)]
        
        # Create user-item matrix
        self.user_ids = sorted(filtered_df['userId'].unique())
        self.movie_ids = sorted(filtered_df['movieId'].unique())
        
        for idx, uid in enumerate(self.user_ids):
            self.user_to_idx[uid] = idx
            self.idx_to_user[idx] = uid
        
        for idx, mid in enumerate(self.movie_ids):
            self.movie_to_idx[mid] = idx
            self.idx_to_movie[idx] = mid
        
        # Build sparse matrix
        n_users = len(self.user_ids)
        n_items = len(self.movie_ids)
        
        rows = filtered_df['userId'].map(self.user_to_idx).values
        cols = filtered_df['movieId'].map(self.movie_to_idx).values
        data = filtered_df['rating'].values
        
        self.user_item_matrix = sparse.csr_matrix(
            (data, (rows, cols)), shape=(n_users, n_items)
        ).toarray()
        
        # Compute item-item similarity
        self._compute_item_similarity()
        
        self.is_fitted = True
        return self
    
    def _compute_item_similarity(self) -> None:
        """Compute item-item cosine similarity matrix."""
        # Transpose to get item-user matrix
        item_user_matrix = self.user_item_matrix.T
        
        # Replace 0s with NaN for mean calculation
        item_user_matrix = np.where(
            item_user_matrix == 0, np.nan, item_user_matrix
        )
        
        # Mean center the ratings
        item_means = np.nanmean(item_user_matrix, axis=1, keepdims=True)
        item_user_centered = np.nan_to_num(item_user_matrix - item_means)
        
        # Compute cosine similarity
        self.item_similarity = cosine_similarity(item_user_centered)
        
        # Zero out diagonal
        np.fill_diagonal(self.item_similarity, 0)
    
    def get_similar_items(self, movie_id: int, n: int = 10) -> List[Dict]:
        """
        Get items similar to a given movie.
        
        Args:
            movie_id: Movie ID
            n: Number of similar items
            
        Returns:
            List of similar items with scores
        """
        if not self.is_fitted or movie_id not in self.movie_to_idx:
            return []
        
        idx = self.movie_to_idx[movie_id]
        similarities = self.item_similarity[idx]
        
        # Get top-n similar items
        similar_indices = np.argsort(similarities)[::-1][:n]
        
        results = []
        for sim_idx in similar_indices:
            sim_movie_id = self.idx_to_movie[sim_idx]
            
            movie_info = self._get_movie_info(sim_movie_id)
            movie_info['similarity'] = float(similarities[sim_idx])
            results.append(movie_info)
        
        return results
    
    def predict_rating(self, user_id: int, movie_id: int) -> Optional[float]:
        """
        Predict rating for a user-movie pair.
        
        Args:
            user_id: User ID
            movie_id: Movie ID to predict rating for
            
        Returns:
            Predicted rating or None
        """
        if not self.is_fitted:
            return None
        
        if user_id not in self.user_to_idx or movie_id not in self.movie_to_idx:
            return None
        
        user_idx = self.user_to_idx[user_id]
        movie_idx = self.movie_to_idx[movie_id]
        
        # Get user's ratings
        user_ratings = self.user_item_matrix[user_idx]
        rated_mask = user_ratings > 0
        
        if not np.any(rated_mask):
            return None
        
        # Get similarities to rated items
        similarities = self.item_similarity[movie_idx]
        
        # Use top-k similar items that user has rated
        rated_indices = np.where(rated_mask)[0]
        rated_similarities = similarities[rated_indices]
        
        # Get top-k
        if len(rated_indices) > self.k:
            top_k_indices = np.argsort(rated_similarities)[::-1][:self.k]
            rated_indices = rated_indices[top_k_indices]
            rated_similarities = rated_similarities[top_k_indices]
        
        # Weighted average
        pos_mask = rated_similarities > 0
        if not np.any(pos_mask):
            return None
        
        weights = rated_similarities[pos_mask]
        ratings = user_ratings[rated_indices[pos_mask]]
        
        predicted = np.sum(weights * ratings) / np.sum(weights)
        
        # Clip to valid range
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
            # Cold start: return popular items
            return self._get_popular_items(n, exclude)
        
        user_idx = self.user_to_idx[user_id]
        user_ratings = self.user_item_matrix[user_idx]
        
        # Add already rated movies to exclude
        rated_indices = np.where(user_ratings > 0)[0]
        rated_movie_ids = {self.idx_to_movie[idx] for idx in rated_indices}
        exclude = exclude.union(rated_movie_ids)
        
        # Predict ratings for unrated movies
        predictions = []
        for movie_idx in range(len(self.movie_ids)):
            movie_id = self.idx_to_movie[movie_idx]
            
            if movie_id in exclude:
                continue
            
            pred = self._predict_for_idx(user_idx, movie_idx, user_ratings, rated_indices)
            if pred is not None:
                predictions.append((movie_id, pred))
        
        # Sort by predicted rating
        predictions.sort(key=lambda x: x[1], reverse=True)
        
        # Return top-n
        results = []
        for movie_id, score in predictions[:n]:
            movie_info = self._get_movie_info(movie_id)
            movie_info['score'] = float(score)
            movie_info['method'] = 'item_based'
            results.append(movie_info)
        
        return results
    
    def _predict_for_idx(self, user_idx: int, movie_idx: int,
                         user_ratings: np.ndarray,
                         rated_indices: np.ndarray) -> Optional[float]:
        """Internal prediction method using indices."""
        if len(rated_indices) == 0:
            return None
        
        similarities = self.item_similarity[movie_idx, rated_indices]
        
        # Get top-k similar items
        if len(rated_indices) > self.k:
            top_k_pos = np.argsort(similarities)[::-1][:self.k]
            similarities = similarities[top_k_pos]
            rated_indices = rated_indices[top_k_pos]
        
        pos_mask = similarities > 0
        if not np.any(pos_mask):
            return None
        
        weights = similarities[pos_mask]
        ratings = user_ratings[rated_indices[pos_mask]]
        
        return float(np.sum(weights * ratings) / np.sum(weights))
    
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
