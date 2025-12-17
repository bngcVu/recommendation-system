"""
Hybrid recommendation model.
Combines Content-Based and Collaborative Filtering approaches.
"""
import numpy as np
from typing import List, Dict, Optional, Set, Tuple
import pandas as pd


class HybridModel:
    """Hybrid model combining multiple recommendation approaches."""
    
    def __init__(self, 
                 content_weight: float = 0.3,
                 item_weight: float = 0.35,
                 user_weight: float = 0.35):
        """
        Initialize hybrid model with weights.
        
        Args:
            content_weight: Weight for content-based recommendations
            item_weight: Weight for item-based collaborative filtering
            user_weight: Weight for user-based collaborative filtering
        """
        # Normalize weights
        total = content_weight + item_weight + user_weight
        self.content_weight = content_weight / total
        self.item_weight = item_weight / total
        self.user_weight = user_weight / total
        
        self.content_model = None
        self.item_model = None
        self.user_model = None
        
        self.movies_df: Optional[pd.DataFrame] = None
        self.ratings_df: Optional[pd.DataFrame] = None
        self.is_fitted: bool = False
    
    def fit(self, movies_df: pd.DataFrame, 
            ratings_df: pd.DataFrame,
            content_model=None,
            item_model=None,
            user_model=None) -> 'HybridModel':
        """
        Fit the hybrid model.
        
        Args:
            movies_df: Movies dataframe
            ratings_df: Ratings dataframe
            content_model: Pre-fitted content-based model (optional)
            item_model: Pre-fitted item-based model (optional)
            user_model: Pre-fitted user-based model (optional)
            
        Returns:
            Self for chaining
        """
        self.movies_df = movies_df
        self.ratings_df = ratings_df
        
        # Fit or use provided models
        if content_model is not None:
            self.content_model = content_model
        else:
            from app.models.content_based import ContentBasedModel
            self.content_model = ContentBasedModel()
            self.content_model.fit(movies_df)
        
        if item_model is not None:
            self.item_model = item_model
        else:
            from app.models.item_based import ItemBasedModel
            self.item_model = ItemBasedModel()
            self.item_model.fit(ratings_df, movies_df)
        
        if user_model is not None:
            self.user_model = user_model
        else:
            from app.models.user_based import UserBasedModel
            self.user_model = UserBasedModel()
            self.user_model.fit(ratings_df, movies_df)
        
        self.is_fitted = True
        return self
    
    def predict_rating(self, user_id: int, movie_id: int,
                       user_rated_movies: Optional[List[Dict]] = None) -> Optional[float]:
        """
        Predict rating using weighted average of models.
        
        Args:
            user_id: User ID
            movie_id: Movie ID
            user_rated_movies: User's rated movies for content-based
            
        Returns:
            Predicted rating
        """
        if not self.is_fitted:
            return None
        
        predictions = []
        weights = []
        
        # Content-based prediction
        if self.content_model is not None and user_rated_movies:
            cb_pred = self.content_model.predict_rating(
                user_id, movie_id, user_rated_movies
            )
            if cb_pred is not None:
                predictions.append(cb_pred)
                weights.append(self.content_weight)
        
        # Item-based prediction
        if self.item_model is not None:
            ib_pred = self.item_model.predict_rating(user_id, movie_id)
            if ib_pred is not None:
                predictions.append(ib_pred)
                weights.append(self.item_weight)
        
        # User-based prediction
        if self.user_model is not None:
            ub_pred = self.user_model.predict_rating(user_id, movie_id)
            if ub_pred is not None:
                predictions.append(ub_pred)
                weights.append(self.user_weight)
        
        if not predictions:
            return None
        
        # Weighted average
        weights = np.array(weights)
        weights = weights / weights.sum()
        predicted = np.average(predictions, weights=weights)
        
        return float(np.clip(predicted, 0.5, 5.0))
    
    def recommend(self, user_id: int, n: int = 10,
                  exclude: Optional[Set[int]] = None,
                  user_rated_movies: Optional[List[Dict]] = None) -> List[Dict]:
        """
        Get hybrid recommendations.
        
        Args:
            user_id: User ID
            n: Number of recommendations
            exclude: Movie IDs to exclude
            user_rated_movies: User's rated movies
            
        Returns:
            List of recommended movies
        """
        if not self.is_fitted:
            return []
        
        exclude = exclude or set()
        
        # Get recommendations from each model
        all_scores: Dict[int, Dict] = {}
        
        # Content-based recommendations
        if self.content_model is not None:
            if user_rated_movies is None:
                user_rated_movies = self._get_user_ratings(user_id)
            
            cb_recs = self.content_model.recommend_for_user(
                user_id, user_rated_movies, n=n*2, exclude=exclude
            )
            for rec in cb_recs:
                movie_id = rec['movieId']
                if movie_id not in all_scores:
                    all_scores[movie_id] = {
                        'movieId': movie_id,
                        'title': rec['title'],
                        'genres': rec['genres'],
                        'avgRating': rec.get('avgRating', 0),
                        'scores': {},
                        'total_weight': 0
                    }
                all_scores[movie_id]['scores']['content'] = rec.get('score', 0)
                all_scores[movie_id]['total_weight'] += self.content_weight
        
        # Item-based recommendations
        if self.item_model is not None:
            ib_recs = self.item_model.recommend(user_id, n=n*2, exclude=exclude)
            for rec in ib_recs:
                movie_id = rec['movieId']
                if movie_id not in all_scores:
                    all_scores[movie_id] = {
                        'movieId': movie_id,
                        'title': rec['title'],
                        'genres': rec['genres'],
                        'avgRating': rec.get('avgRating', 0),
                        'scores': {},
                        'total_weight': 0
                    }
                all_scores[movie_id]['scores']['item'] = rec.get('score', 0)
                all_scores[movie_id]['total_weight'] += self.item_weight
        
        # User-based recommendations
        if self.user_model is not None:
            ub_recs = self.user_model.recommend(user_id, n=n*2, exclude=exclude)
            for rec in ub_recs:
                movie_id = rec['movieId']
                if movie_id not in all_scores:
                    all_scores[movie_id] = {
                        'movieId': movie_id,
                        'title': rec['title'],
                        'genres': rec['genres'],
                        'avgRating': rec.get('avgRating', 0),
                        'scores': {},
                        'total_weight': 0
                    }
                all_scores[movie_id]['scores']['user'] = rec.get('score', 0)
                all_scores[movie_id]['total_weight'] += self.user_weight
        
        # Compute final scores
        results = []
        for movie_id, data in all_scores.items():
            if movie_id in exclude:
                continue
            
            scores = data['scores']
            
            # Weighted sum of available scores
            final_score = 0
            weight_sum = 0
            
            if 'content' in scores:
                final_score += scores['content'] * self.content_weight
                weight_sum += self.content_weight
            if 'item' in scores:
                final_score += scores['item'] * self.item_weight
                weight_sum += self.item_weight
            if 'user' in scores:
                final_score += scores['user'] * self.user_weight
                weight_sum += self.user_weight
            
            if weight_sum > 0:
                final_score /= weight_sum
            
            results.append({
                'movieId': movie_id,
                'title': data['title'],
                'genres': data['genres'],
                'avgRating': data['avgRating'],
                'score': float(final_score),
                'method': 'hybrid',
                'component_scores': scores
            })
        
        # Sort by final score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results[:n]
    
    def get_similar_movies(self, movie_id: int, n: int = 10) -> List[Dict]:
        """
        Get similar movies using hybrid approach.
        
        Args:
            movie_id: Movie ID
            n: Number of similar movies
            
        Returns:
            List of similar movies
        """
        if not self.is_fitted:
            return []
        
        all_similar: Dict[int, Dict] = {}
        
        # Content-based similar
        if self.content_model is not None:
            cb_similar = self.content_model.get_similar_movies(movie_id, n=n*2)
            for movie in cb_similar:
                mid = movie['movieId']
                if mid not in all_similar:
                    all_similar[mid] = {
                        'movieId': mid,
                        'title': movie['title'],
                        'genres': movie['genres'],
                        'avgRating': movie.get('avgRating', 0),
                        'similarities': {}
                    }
                all_similar[mid]['similarities']['content'] = movie['similarity']
        
        # Item-based similar
        if self.item_model is not None:
            ib_similar = self.item_model.get_similar_items(movie_id, n=n*2)
            for movie in ib_similar:
                mid = movie['movieId']
                if mid not in all_similar:
                    all_similar[mid] = {
                        'movieId': mid,
                        'title': movie['title'],
                        'genres': movie.get('genres', []),
                        'avgRating': movie.get('avgRating', 0),
                        'similarities': {}
                    }
                all_similar[mid]['similarities']['item'] = movie['similarity']
        
        # Compute hybrid similarity
        results = []
        for mid, data in all_similar.items():
            sims = data['similarities']
            
            hybrid_sim = 0
            weight_sum = 0
            
            if 'content' in sims:
                hybrid_sim += sims['content'] * self.content_weight
                weight_sum += self.content_weight
            if 'item' in sims:
                hybrid_sim += sims['item'] * self.item_weight
                weight_sum += self.item_weight
            
            if weight_sum > 0:
                hybrid_sim /= weight_sum
            
            results.append({
                'movieId': mid,
                'title': data['title'],
                'genres': data['genres'],
                'avgRating': data['avgRating'],
                'similarity': float(hybrid_sim),
                'method': 'hybrid'
            })
        
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:n]
    
    def explain_recommendation(self, user_id: int, movie_id: int,
                               user_rated_movies: Optional[List[Dict]] = None) -> Dict:
        """
        Explain why a movie was recommended.
        
        Args:
            user_id: User ID
            movie_id: Movie ID
            user_rated_movies: User's rated movies
            
        Returns:
            Explanation dictionary
        """
        if not self.is_fitted:
            return {}
        
        explanation = {
            'movieId': movie_id,
            'methods': []
        }
        
        if user_rated_movies is None:
            user_rated_movies = self._get_user_ratings(user_id)
        
        # Content-based explanation
        if self.content_model is not None and user_rated_movies:
            # Find which rated movies are similar
            similar_rated = []
            for rated in user_rated_movies:
                if rated['movieId'] in self.content_model.movie_id_to_idx:
                    rated_idx = self.content_model.movie_id_to_idx[rated['movieId']]
                    movie_idx = self.content_model.movie_id_to_idx.get(movie_id)
                    if movie_idx is not None:
                        sim = self.content_model.similarity_matrix[movie_idx, rated_idx]
                        if sim > 0.1:
                            similar_rated.append({
                                'movieId': rated['movieId'],
                                'similarity': float(sim),
                                'rating': rated['rating']
                            })
            
            similar_rated.sort(key=lambda x: x['similarity'], reverse=True)
            explanation['methods'].append({
                'method': 'content_based',
                'weight': self.content_weight,
                'reason': f'Similar to {len(similar_rated)} movies you liked',
                'similar_movies': similar_rated[:5]
            })
        
        # Item-based explanation
        if self.item_model is not None and movie_id in self.item_model.movie_to_idx:
            explanation['methods'].append({
                'method': 'item_based',
                'weight': self.item_weight,
                'reason': 'Users who rated movies you rated also rated this highly'
            })
        
        # User-based explanation
        if self.user_model is not None and user_id in self.user_model.user_to_idx:
            similar_users = self.user_model.get_similar_users(user_id, n=5)
            explanation['methods'].append({
                'method': 'user_based',
                'weight': self.user_weight,
                'reason': f'Recommended by {len(similar_users)} users similar to you',
                'similar_user_count': len(similar_users)
            })
        
        # Predicted score
        pred = self.predict_rating(user_id, movie_id, user_rated_movies)
        if pred is not None:
            explanation['predicted_rating'] = pred
        
        return explanation
    
    def _get_user_ratings(self, user_id: int) -> List[Dict]:
        """Get user's ratings from dataframe."""
        if self.ratings_df is None:
            return []
        
        user_ratings = self.ratings_df[self.ratings_df['userId'] == user_id]
        return [
            {'movieId': int(row['movieId']), 'rating': float(row['rating'])}
            for _, row in user_ratings.iterrows()
        ]
    
    def set_weights(self, content_weight: float, 
                    item_weight: float, 
                    user_weight: float) -> None:
        """
        Update model weights.
        
        Args:
            content_weight: Weight for content-based
            item_weight: Weight for item-based
            user_weight: Weight for user-based
        """
        total = content_weight + item_weight + user_weight
        self.content_weight = content_weight / total
        self.item_weight = item_weight / total
        self.user_weight = user_weight / total
