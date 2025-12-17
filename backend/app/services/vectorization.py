"""
Vectorization service for creating TF-IDF vectors and embeddings.
"""
import numpy as np
import pandas as pd
from typing import List, Tuple, Optional
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize


class Vectorizer:
    """Service for vectorizing movie data."""
    
    def __init__(self):
        """Initialize vectorizer."""
        self.tfidf_vectorizer: Optional[TfidfVectorizer] = None
        self.sentence_model = None
        self._load_sentence_model()
    
    def _load_sentence_model(self):
        """Lazily load sentence transformer model."""
        try:
            from sentence_transformers import SentenceTransformer
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        except ImportError:
            print("Warning: sentence-transformers not installed. Embeddings will not be available.")
            self.sentence_model = None
        except Exception as e:
            print(f"Warning: Could not load sentence transformer: {e}")
            self.sentence_model = None
    
    def tfidf_vectorize(self, genres_list: List[List[str]], 
                        max_features: int = 100) -> Tuple[sparse.csr_matrix, List[str]]:
        """
        Create TF-IDF vectors from movie genres.
        
        Args:
            genres_list: List of genre lists for each movie
            max_features: Maximum number of features
            
        Returns:
            Tuple of (TF-IDF matrix, feature names)
        """
        # Convert genre lists to space-separated strings
        genres_text = [' '.join(genres) for genres in genres_list]
        
        # Create TF-IDF vectorizer
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=max_features,
            token_pattern=r'(?u)\b[\w-]+\b',  # Include hyphenated genres
            lowercase=True
        )
        
        # Fit and transform
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(genres_text)
        feature_names = self.tfidf_vectorizer.get_feature_names_out().tolist()
        
        return tfidf_matrix, feature_names
    
    def create_embeddings(self, texts: List[str], 
                          batch_size: int = 32) -> Optional[np.ndarray]:
        """
        Create sentence embeddings for movie titles and descriptions.
        
        Args:
            texts: List of text strings to embed
            batch_size: Batch size for encoding
            
        Returns:
            Numpy array of embeddings or None if model not available
        """
        if self.sentence_model is None:
            print("Sentence model not available, returning None")
            return None
        
        embeddings = self.sentence_model.encode(
            texts, 
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        return embeddings
    
    def create_movie_embeddings(self, movies_df: pd.DataFrame) -> Optional[np.ndarray]:
        """
        Create embeddings for movies using title and genres.
        
        Args:
            movies_df: Movies dataframe with 'title' and 'genres' columns
            
        Returns:
            Numpy array of movie embeddings
        """
        # Combine title and genres for richer representation
        texts = []
        for _, row in movies_df.iterrows():
            title = row.get('cleanTitle', row.get('title', ''))
            genres = row.get('genres', [])
            if isinstance(genres, list):
                genres_str = ', '.join(genres)
            else:
                genres_str = str(genres)
            
            text = f"{title}. Genres: {genres_str}"
            texts.append(text)
        
        return self.create_embeddings(texts)
    
    @staticmethod
    def create_user_item_matrix(ratings_df: pd.DataFrame, 
                                 fill_value: float = 0) -> Tuple[sparse.csr_matrix, List[int], List[int]]:
        """
        Create user-item rating matrix.
        
        Args:
            ratings_df: Ratings dataframe with userId, movieId, rating columns
            fill_value: Value to fill for missing ratings
            
        Returns:
            Tuple of (sparse matrix, user_ids, movie_ids)
        """
        # Get unique users and movies
        user_ids = sorted(ratings_df['userId'].unique())
        movie_ids = sorted(ratings_df['movieId'].unique())
        
        # Create mappings
        user_to_idx = {uid: idx for idx, uid in enumerate(user_ids)}
        movie_to_idx = {mid: idx for idx, mid in enumerate(movie_ids)}
        
        # Create sparse matrix
        n_users = len(user_ids)
        n_movies = len(movie_ids)
        
        rows = ratings_df['userId'].map(user_to_idx).values
        cols = ratings_df['movieId'].map(movie_to_idx).values
        data = ratings_df['rating'].values
        
        matrix = sparse.csr_matrix(
            (data, (rows, cols)), 
            shape=(n_users, n_movies)
        )
        
        return matrix, user_ids, movie_ids
    
    @staticmethod
    def compute_cosine_similarity(matrix: np.ndarray) -> np.ndarray:
        """
        Compute cosine similarity matrix.
        
        Args:
            matrix: Feature matrix (n_samples x n_features)
            
        Returns:
            Similarity matrix (n_samples x n_samples)
        """
        # Normalize rows
        normalized = normalize(matrix, axis=1, norm='l2')
        
        # Compute similarity
        if sparse.issparse(normalized):
            similarity = normalized @ normalized.T
            similarity = similarity.toarray()
        else:
            similarity = normalized @ normalized.T
        
        return similarity
    
    @staticmethod
    def compute_pearson_correlation(matrix: np.ndarray, 
                                     min_common: int = 3) -> np.ndarray:
        """
        Compute Pearson correlation similarity.
        
        Args:
            matrix: Rating matrix (n_users x n_items or n_items x n_users)
            min_common: Minimum common ratings required
            
        Returns:
            Similarity matrix
        """
        if sparse.issparse(matrix):
            matrix = matrix.toarray()
        
        n = matrix.shape[0]
        similarity = np.zeros((n, n))
        
        for i in range(n):
            for j in range(i, n):
                # Find common rated items
                mask_i = matrix[i] != 0
                mask_j = matrix[j] != 0
                common = mask_i & mask_j
                
                if common.sum() >= min_common:
                    vals_i = matrix[i, common]
                    vals_j = matrix[j, common]
                    
                    # Center the values
                    vals_i = vals_i - vals_i.mean()
                    vals_j = vals_j - vals_j.mean()
                    
                    # Compute correlation
                    denom = np.sqrt(np.sum(vals_i**2) * np.sum(vals_j**2))
                    if denom > 0:
                        corr = np.sum(vals_i * vals_j) / denom
                        similarity[i, j] = corr
                        similarity[j, i] = corr
        
        return similarity
    
    def get_tfidf_vector(self, genres: List[str]) -> Optional[np.ndarray]:
        """
        Get TF-IDF vector for a given genre list.
        
        Args:
            genres: List of genres
            
        Returns:
            TF-IDF vector or None if vectorizer not fitted
        """
        if self.tfidf_vectorizer is None:
            return None
        
        genres_text = ' '.join(genres)
        vector = self.tfidf_vectorizer.transform([genres_text])
        return vector.toarray()[0]
