"""
Script to download movie dataset from Kaggle.
Run: python scripts/download_data.py
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def download_dataset():
    """Download movie recommendation dataset from Kaggle."""
    try:
        import kagglehub
        
        print("Downloading movie recommendation dataset from Kaggle...")
        
        # Download latest version
        path = kagglehub.dataset_download("parasharmanas/movie-recommendation-system")
        
        print(f"✓ Dataset downloaded to: {path}")
        
        # Copy to data/raw directory
        import shutil
        
        raw_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'raw')
        os.makedirs(raw_dir, exist_ok=True)
        
        # Copy CSV files
        for file in os.listdir(path):
            if file.endswith('.csv'):
                src = os.path.join(path, file)
                dst = os.path.join(raw_dir, file)
                shutil.copy2(src, dst)
                print(f"  Copied: {file}")
        
        print(f"✓ Data copied to: {raw_dir}")
        
        return raw_dir
        
    except ImportError:
        print("Error: kagglehub not installed. Run: pip install kagglehub")
        return None
    except Exception as e:
        print(f"Error downloading dataset: {e}")
        return None


def verify_dataset():
    """Verify that required files exist."""
    raw_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'raw')
    
    required_files = ['movies.csv', 'ratings.csv']
    missing = []
    
    for file in required_files:
        path = os.path.join(raw_dir, file)
        if os.path.exists(path):
            size = os.path.getsize(path) / 1024 / 1024  # MB
            print(f"  ✓ {file}: {size:.2f} MB")
        else:
            missing.append(file)
            print(f"  ✗ {file}: Missing")
    
    if missing:
        print(f"\n⚠ Missing files: {', '.join(missing)}")
        return False
    
    print("\n✓ All required files present")
    return True


if __name__ == '__main__':
    print("=" * 50)
    print("Movie Recommendation Dataset Downloader")
    print("=" * 50)
    
    download_dataset()
    
    print("\nVerifying dataset...")
    verify_dataset()
