"""
Data processing service for cleaning and preparing movie data.
"""
import pandas as pd
import numpy as np
import re
from typing import Tuple, Optional
from datetime import datetime


class DataProcessor:
    """Service for processing and cleaning movie data."""
    
    @staticmethod
    def load_csv_data(movies_path: str, ratings_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load movies and ratings data from CSV files.
        
        Args:
            movies_path: Path to movies.csv
            ratings_path: Path to ratings.csv
            
        Returns:
            Tuple of (movies_df, ratings_df)
        """
        movies_df = pd.read_csv(movies_path)
        ratings_df = pd.read_csv(ratings_path)
        return movies_df, ratings_df
    
    @staticmethod
    def handle_missing_values(df: pd.DataFrame, strategy: str = 'drop') -> pd.DataFrame:
        """
        Handle missing values in dataframe.
        
        Args:
            df: Input dataframe
            strategy: 'drop' to remove rows, 'fill' to fill with defaults
            
        Returns:
            Cleaned dataframe
        """
        if strategy == 'drop':
            return df.dropna()
        elif strategy == 'fill':
            # Fill numeric columns with median
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                df[col] = df[col].fillna(df[col].median())
            
            # Fill string columns with empty string
            string_cols = df.select_dtypes(include=['object']).columns
            for col in string_cols:
                df[col] = df[col].fillna('')
            
            return df
        return df
    
    @staticmethod
    def remove_duplicates(df: pd.DataFrame, subset: Optional[list] = None, 
                          keep: str = 'last') -> pd.DataFrame:
        """
        Remove duplicate rows from dataframe.
        
        Args:
            df: Input dataframe
            subset: Columns to consider for duplicates
            keep: 'first', 'last', or False
            
        Returns:
            Dataframe with duplicates removed
        """
        return df.drop_duplicates(subset=subset, keep=keep)
    
    @staticmethod
    def handle_outliers(df: pd.DataFrame, column: str, 
                        lower_bound: float, upper_bound: float) -> pd.DataFrame:
        """
        Handle outliers by clipping values to specified bounds.
        
        Args:
            df: Input dataframe
            column: Column to process
            lower_bound: Minimum allowed value
            upper_bound: Maximum allowed value
            
        Returns:
            Dataframe with outliers clipped
        """
        df[column] = df[column].clip(lower=lower_bound, upper=upper_bound)
        return df
    
    @staticmethod
    def normalize_ratings(ratings: pd.Series, min_val: float = 0.5, 
                          max_val: float = 5.0) -> pd.Series:
        """
        Normalize ratings to [0, 1] range.
        
        Args:
            ratings: Rating series
            min_val: Original minimum rating
            max_val: Original maximum rating
            
        Returns:
            Normalized ratings
        """
        return (ratings - min_val) / (max_val - min_val)
    
    @staticmethod
    def parse_genres(genres_str: str, separator: str = '|') -> list:
        """
        Parse genres string into list.
        
        Args:
            genres_str: Genres string like "Action|Comedy|Drama"
            separator: Character separating genres
            
        Returns:
            List of genre strings
        """
        if pd.isna(genres_str) or genres_str == '(no genres listed)':
            return []
        return [g.strip() for g in genres_str.split(separator) if g.strip()]
    
    @staticmethod
    def extract_year_from_title(title: str) -> Tuple[str, Optional[int]]:
        """
        Extract year from movie title.
        
        Args:
            title: Movie title like "Toy Story (1995)"
            
        Returns:
            Tuple of (clean_title, year)
        """
        match = re.search(r'\((\d{4})\)\s*$', title)
        if match:
            year = int(match.group(1))
            clean_title = re.sub(r'\s*\(\d{4}\)\s*$', '', title)
            return clean_title.strip(), year
        return title.strip(), None
    
    @classmethod
    def process_movies(cls, movies_df: pd.DataFrame) -> pd.DataFrame:
        """
        Process movies dataframe: clean and add features.
        
        Args:
            movies_df: Raw movies dataframe
            
        Returns:
            Processed movies dataframe
        """
        # Handle missing values
        movies_df = cls.handle_missing_values(movies_df, strategy='fill')
        
        # Remove duplicates
        movies_df = cls.remove_duplicates(movies_df, subset=['movieId'])
        
        # Parse genres
        movies_df['genres'] = movies_df['genres'].apply(cls.parse_genres)
        
        # Extract year from title
        title_year = movies_df['title'].apply(cls.extract_year_from_title)
        movies_df['cleanTitle'] = title_year.apply(lambda x: x[0])
        movies_df['year'] = title_year.apply(lambda x: x[1])
        
        # Add timestamps
        now = datetime.utcnow()
        movies_df['createdAt'] = now
        movies_df['updatedAt'] = now
        
        return movies_df
    
    @classmethod
    def process_ratings(cls, ratings_df: pd.DataFrame) -> pd.DataFrame:
        """
        Process ratings dataframe.
        
        Args:
            ratings_df: Raw ratings dataframe
            
        Returns:
            Processed ratings dataframe
        """
        # Handle missing values
        ratings_df = cls.handle_missing_values(ratings_df, strategy='drop')
        
        # Remove duplicate ratings (keep latest)
        ratings_df = cls.remove_duplicates(
            ratings_df, 
            subset=['userId', 'movieId'], 
            keep='last'
        )
        
        # Clip outlier ratings
        ratings_df = cls.handle_outliers(ratings_df, 'rating', 0.5, 5.0)
        
        # Convert timestamp to datetime
        if 'timestamp' in ratings_df.columns:
            ratings_df['timestamp'] = pd.to_datetime(
                ratings_df['timestamp'], 
                unit='s'
            )
        
        # Add created timestamp
        ratings_df['createdAt'] = datetime.utcnow()
        
        return ratings_df
    
    @staticmethod
    def calculate_movie_stats(movies_df: pd.DataFrame, 
                              ratings_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate average rating and count for each movie.
        
        Args:
            movies_df: Movies dataframe
            ratings_df: Ratings dataframe
            
        Returns:
            Movies dataframe with added stats
        """
        # Calculate stats per movie
        stats = ratings_df.groupby('movieId').agg({
            'rating': ['mean', 'count']
        }).round(2)
        stats.columns = ['avgRating', 'ratingCount']
        stats = stats.reset_index()
        
        # Merge with movies
        movies_df = movies_df.merge(stats, on='movieId', how='left')
        movies_df['avgRating'] = movies_df['avgRating'].fillna(0)
        movies_df['ratingCount'] = movies_df['ratingCount'].fillna(0).astype(int)
        
        return movies_df
    
    @staticmethod
    def create_user_profiles(ratings_df: pd.DataFrame, 
                             movies_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create user profiles from ratings data.
        
        Args:
            ratings_df: Ratings dataframe
            movies_df: Movies dataframe (with genres)
            
        Returns:
            User profiles dataframe
        """
        # Create movie genres lookup
        movie_genres = movies_df.set_index('movieId')['genres'].to_dict()
        
        users = []
        for user_id in ratings_df['userId'].unique():
            user_ratings = ratings_df[ratings_df['userId'] == user_id]
            rated_movies = user_ratings['movieId'].tolist()
            
            # Calculate favorite genres
            all_genres = []
            for movie_id in rated_movies:
                if movie_id in movie_genres:
                    all_genres.extend(movie_genres[movie_id])
            
            genre_counts = pd.Series(all_genres).value_counts()
            favorite_genres = genre_counts.head(5).index.tolist() if len(genre_counts) > 0 else []
            
            users.append({
                'userId': user_id,
                'username': f'user_{user_id}',
                'ratedMovies': rated_movies,
                'watchedMovies': rated_movies,
                'preferences': {
                    'favoriteGenres': favorite_genres,
                    'avgRating': float(user_ratings['rating'].mean())
                },
                'createdAt': datetime.utcnow(),
                'updatedAt': datetime.utcnow()
            })
        
        return pd.DataFrame(users)
