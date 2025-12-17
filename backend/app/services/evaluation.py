"""
Model evaluation service for computing recommendation metrics.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Set, Any, Optional
from collections import defaultdict


class ModelEvaluator:
    """Service for evaluating recommendation models."""
    
    @staticmethod
    def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """
        Calculate Root Mean Squared Error.
        
        Args:
            y_true: True ratings
            y_pred: Predicted ratings
            
        Returns:
            RMSE value
        """
        y_true = np.array(y_true)
        y_pred = np.array(y_pred)
        return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
    
    @staticmethod
    def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """
        Calculate Mean Absolute Error.
        
        Args:
            y_true: True ratings
            y_pred: Predicted ratings
            
        Returns:
            MAE value
        """
        y_true = np.array(y_true)
        y_pred = np.array(y_pred)
        return float(np.mean(np.abs(y_true - y_pred)))
    
    @staticmethod
    def precision_at_k(recommendations: List[int], 
                       relevant: Set[int], 
                       k: int) -> float:
        """
        Calculate Precision@K.
        
        Args:
            recommendations: List of recommended item ids
            relevant: Set of relevant (ground truth) item ids
            k: Number of top recommendations to consider
            
        Returns:
            Precision@K value
        """
        if k <= 0:
            return 0.0
        
        top_k = recommendations[:k]
        hits = len(set(top_k) & relevant)
        return float(hits / k)
    
    @staticmethod
    def recall_at_k(recommendations: List[int], 
                    relevant: Set[int], 
                    k: int) -> float:
        """
        Calculate Recall@K.
        
        Args:
            recommendations: List of recommended item ids
            relevant: Set of relevant (ground truth) item ids
            k: Number of top recommendations to consider
            
        Returns:
            Recall@K value
        """
        if len(relevant) == 0:
            return 0.0
        
        top_k = recommendations[:k]
        hits = len(set(top_k) & relevant)
        return float(hits / len(relevant))
    
    @staticmethod
    def f1_at_k(precision: float, recall: float) -> float:
        """
        Calculate F1 score from precision and recall.
        
        Args:
            precision: Precision value
            recall: Recall value
            
        Returns:
            F1 score
        """
        if precision + recall == 0:
            return 0.0
        return 2 * (precision * recall) / (precision + recall)
    
    @staticmethod
    def ndcg_at_k(recommendations: List[int], 
                  relevance_scores: Dict[int, float], 
                  k: int) -> float:
        """
        Calculate Normalized Discounted Cumulative Gain @K.
        
        Args:
            recommendations: List of recommended item ids
            relevance_scores: Dict mapping item id to relevance (rating)
            k: Number of top recommendations to consider
            
        Returns:
            NDCG@K value
        """
        top_k = recommendations[:k]
        
        # Calculate DCG
        dcg = 0.0
        for i, item_id in enumerate(top_k):
            rel = relevance_scores.get(item_id, 0)
            dcg += (2**rel - 1) / np.log2(i + 2)
        
        # Calculate IDCG (ideal DCG)
        ideal_rels = sorted(relevance_scores.values(), reverse=True)[:k]
        idcg = 0.0
        for i, rel in enumerate(ideal_rels):
            idcg += (2**rel - 1) / np.log2(i + 2)
        
        if idcg == 0:
            return 0.0
        
        return float(dcg / idcg)
    
    @staticmethod
    def hit_rate_at_k(recommendations: List[int], 
                      relevant: Set[int], 
                      k: int) -> float:
        """
        Calculate Hit Rate @K (whether at least one item is relevant).
        
        Args:
            recommendations: List of recommended item ids
            relevant: Set of relevant item ids
            k: Number of top recommendations to consider
            
        Returns:
            1.0 if hit, 0.0 otherwise
        """
        top_k = recommendations[:k]
        return 1.0 if len(set(top_k) & relevant) > 0 else 0.0
    
    @staticmethod
    def coverage(recommended_items: Set[int], 
                 all_items: Set[int]) -> float:
        """
        Calculate catalog coverage.
        
        Args:
            recommended_items: Set of all recommended item ids
            all_items: Set of all available item ids
            
        Returns:
            Coverage percentage
        """
        if len(all_items) == 0:
            return 0.0
        return len(recommended_items) / len(all_items)
    
    @classmethod
    def evaluate_model(cls, 
                       model,
                       test_ratings: pd.DataFrame,
                       train_ratings: pd.DataFrame,
                       k_values: List[int] = [5, 10, 20],
                       rating_threshold: float = 3.5) -> Dict[str, Any]:
        """
        Comprehensive model evaluation.
        
        Args:
            model: Recommendation model with predict/recommend methods
            test_ratings: Test set ratings
            train_ratings: Training set ratings (to exclude from recs)
            k_values: List of K values for metrics
            rating_threshold: Threshold for considering item as relevant
            
        Returns:
            Dictionary of evaluation metrics
        """
        metrics = {
            'rmse': 0.0,
            'mae': 0.0,
        }
        
        # Initialize metrics for different K values
        for k in k_values:
            metrics[f'precision@{k}'] = []
            metrics[f'recall@{k}'] = []
            metrics[f'ndcg@{k}'] = []
            metrics[f'hit_rate@{k}'] = []
        
        # Get predictions for rating-based metrics
        y_true = []
        y_pred = []
        
        # Get unique users in test set
        test_users = test_ratings['userId'].unique()
        
        for user_id in test_users:
            user_test = test_ratings[test_ratings['userId'] == user_id]
            user_train = train_ratings[train_ratings['userId'] == user_id]
            
            # Get relevant items (high-rated in test)
            relevant = set(
                user_test[user_test['rating'] >= rating_threshold]['movieId']
            )
            
            # Get items to exclude (already seen in training)
            exclude = set(user_train['movieId'])
            
            # Get predictions for test items
            for _, row in user_test.iterrows():
                try:
                    pred = model.predict_rating(user_id, row['movieId'])
                    if pred is not None:
                        y_true.append(row['rating'])
                        y_pred.append(pred)
                except Exception:
                    pass
            
            # Get recommendations
            try:
                max_k = max(k_values)
                recommendations = model.recommend(user_id, n=max_k, exclude=exclude)
                rec_ids = [r['movieId'] for r in recommendations]
                
                # Relevance scores for NDCG
                relevance_scores = dict(
                    zip(user_test['movieId'], user_test['rating'])
                )
                
                # Calculate metrics for each K
                for k in k_values:
                    metrics[f'precision@{k}'].append(
                        cls.precision_at_k(rec_ids, relevant, k)
                    )
                    metrics[f'recall@{k}'].append(
                        cls.recall_at_k(rec_ids, relevant, k)
                    )
                    metrics[f'ndcg@{k}'].append(
                        cls.ndcg_at_k(rec_ids, relevance_scores, k)
                    )
                    metrics[f'hit_rate@{k}'].append(
                        cls.hit_rate_at_k(rec_ids, relevant, k)
                    )
            except Exception:
                pass
        
        # Aggregate metrics
        if y_true and y_pred:
            metrics['rmse'] = cls.rmse(np.array(y_true), np.array(y_pred))
            metrics['mae'] = cls.mae(np.array(y_true), np.array(y_pred))
        
        for k in k_values:
            for metric_name in ['precision', 'recall', 'ndcg', 'hit_rate']:
                key = f'{metric_name}@{k}'
                if metrics[key]:
                    metrics[key] = float(np.mean(metrics[key]))
                else:
                    metrics[key] = 0.0
        
        # Add F1 scores
        for k in k_values:
            p = metrics[f'precision@{k}']
            r = metrics[f'recall@{k}']
            metrics[f'f1@{k}'] = cls.f1_at_k(p, r)
        
        return metrics
    
    @staticmethod
    def cross_validate(model_class, 
                       data: pd.DataFrame, 
                       k_folds: int = 5,
                       **model_kwargs) -> Dict[str, List[float]]:
        """
        Perform k-fold cross-validation.
        
        Args:
            model_class: Model class to instantiate
            data: Rating data
            k_folds: Number of folds
            **model_kwargs: Arguments to pass to model constructor
            
        Returns:
            Dictionary of metric lists across folds
        """
        from sklearn.model_selection import KFold
        
        kf = KFold(n_splits=k_folds, shuffle=True, random_state=42)
        
        cv_results = defaultdict(list)
        
        for fold, (train_idx, test_idx) in enumerate(kf.split(data)):
            train_data = data.iloc[train_idx]
            test_data = data.iloc[test_idx]
            
            # Train model
            model = model_class(**model_kwargs)
            model.fit(train_data)
            
            # Evaluate
            metrics = ModelEvaluator.evaluate_model(
                model, test_data, train_data
            )
            
            for key, value in metrics.items():
                cv_results[key].append(value)
        
        return dict(cv_results)
