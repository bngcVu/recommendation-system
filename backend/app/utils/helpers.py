"""
Utility helper functions.
"""
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib


def generate_gradient(title: str) -> str:
    """
    Generate CSS gradient string from movie title hash.
    
    Args:
        title: Movie title
        
    Returns:
        CSS linear-gradient string
    """
    hash_val = sum(ord(c) << (5 * i % 20) for i, c in enumerate(title))
    hue1 = abs(hash_val) % 360
    hue2 = (hue1 + 40) % 360
    return f"linear-gradient(135deg, hsl({hue1}, 70%, 35%), hsl({hue2}, 70%, 25%))"


def parse_year_from_title(title: str) -> tuple:
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


def parse_genres(genres_str: str, separator: str = '|') -> List[str]:
    """
    Parse genres string into list.
    
    Args:
        genres_str: Genres string like "Action|Comedy|Drama"
        separator: Character separating genres
        
    Returns:
        List of genre strings
    """
    if not genres_str or genres_str == '(no genres listed)':
        return []
    return [g.strip() for g in genres_str.split(separator) if g.strip()]


def format_timestamp(dt: datetime) -> str:
    """Format datetime to ISO string."""
    if dt is None:
        return None
    return dt.isoformat()


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert value to int."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def paginate_list(items: List, page: int, limit: int) -> Dict:
    """
    Paginate a list of items.
    
    Args:
        items: List to paginate
        page: Current page (1-indexed)
        limit: Items per page
        
    Returns:
        Dict with paginated items and metadata
    """
    total = len(items)
    start = (page - 1) * limit
    end = start + limit
    
    return {
        'items': items[start:end],
        'page': page,
        'limit': limit,
        'total': total,
        'pages': (total + limit - 1) // limit if limit > 0 else 0
    }


def create_hash_id(data: str) -> str:
    """Create a short hash ID from data string."""
    return hashlib.md5(data.encode()).hexdigest()[:12]


def normalize_rating(rating: float, min_val: float = 0.5, max_val: float = 5.0) -> float:
    """Normalize rating to [0, 1] range."""
    return (rating - min_val) / (max_val - min_val)


def denormalize_rating(normalized: float, min_val: float = 0.5, max_val: float = 5.0) -> float:
    """Convert normalized rating back to original range."""
    return normalized * (max_val - min_val) + min_val


def clip_rating(rating: float, min_val: float = 0.5, max_val: float = 5.0) -> float:
    """Clip rating to valid range."""
    return max(min_val, min(max_val, rating))
