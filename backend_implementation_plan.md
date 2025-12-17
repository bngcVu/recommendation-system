# Backend Implementation Plan - Hệ Thống Recommendation Phim

## Tổng quan

Xây dựng backend cho hệ thống gợi ý phim sử dụng Python/Flask và **MongoDB**, bao gồm xử lý dữ liệu, xây dựng mô hình recommendation, lưu trữ dữ liệu, và cung cấp API cho frontend.

---

## 1. Cấu trúc thư mục Backend

```
backend/
├── app/
│   ├── __init__.py
│   ├── config.py              # Cấu hình ứng dụng & MongoDB
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py      # MongoDB connection
│   │   ├── schemas.py         # MongoDB schemas/collections
│   │   └── repositories/
│   │       ├── movie_repo.py  # Movie CRUD operations
│   │       ├── user_repo.py   # User CRUD operations
│   │       ├── rating_repo.py # Rating CRUD operations
│   │       └── model_repo.py  # Model data storage
│   ├── models/
│   │   ├── __init__.py
│   │   ├── content_based.py   # Content-based filtering
│   │   ├── item_based.py      # Item-based collaborative filtering
│   │   ├── user_based.py      # User-based collaborative filtering
│   │   └── hybrid.py          # Hybrid model
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── recommendation.py  # API gợi ý phim
│   │   ├── movies.py          # API quản lý phim
│   │   └── users.py           # API quản lý user
│   ├── services/
│   │   ├── __init__.py
│   │   ├── data_processing.py # Xử lý dữ liệu
│   │   ├── vectorization.py   # TF-IDF, embeddings
│   │   └── evaluation.py      # Đánh giá mô hình
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── data/
│   ├── raw/                   # Dữ liệu gốc (CSV)
│   └── processed/             # Dữ liệu đã xử lý
├── notebooks/
│   ├── 01_data_preparation.ipynb    # Thu thập, làm sạch, chuẩn bị dữ liệu
│   ├── 02_data_exploration.ipynb    # Phân tích & trực quan hóa
│   ├── 03_model_training.ipynb      # Train 4 mô hình
│   ├── 04_model_evaluation.ipynb    # Đánh giá & lưu metrics lên MongoDB
│   └── utils/
│       └── mongo_helper.py          # Helper functions cho MongoDB
├── tests/
│   └── test_models.py
├── requirements.txt
├── docker-compose.yml         # MongoDB container
└── run.py                     # Entry point
```

---

## 2. Jupyter Notebooks Workflow

> [!IMPORTANT]
> Toàn bộ quá trình chuẩn bị dữ liệu, training và đánh giá được thực hiện trong **Jupyter Notebooks**. Kết quả đánh giá sẽ được lưu lên **MongoDB**.

### 2.1 Notebook 1: Data Preparation

#### [NEW] `notebooks/01_data_preparation.ipynb`

**Nội dung:**

1. **Download dataset** từ Kaggle
2. **Load CSV files** (movies.csv, ratings.csv)
3. **Làm sạch dữ liệu**:
    - Xử lý missing values
    - Loại bỏ duplicates
    - Xử lý outliers
4. **Feature engineering**:
    - Parse genres thành list
    - Extract year từ title
    - Tính avgRating và ratingCount cho mỗi phim
5. **Vector hóa**:
    - TF-IDF cho genres
    - Embeddings cho title + genres
6. **Import dữ liệu lên MongoDB**:
    - Collection `movies`
    - Collection `users`
    - Collection `ratings`

```python
# Ví dụ import data lên MongoDB
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017')
db = client['movie_recommendation']

# Insert movies
movies_data = movies_df.to_dict('records')
db.movies.insert_many(movies_data)

# Insert ratings
ratings_data = ratings_df.to_dict('records')
db.ratings.insert_many(ratings_data)
```

### 2.2 Notebook 2: Data Exploration

#### [NEW] `notebooks/02_data_exploration.ipynb`

**Nội dung:**

1. Thống kê cơ bản
2. Phân bố rating (histogram)
3. Top genres (bar chart)
4. Top movies by rating count
5. Rating heatmap (sample)
6. User activity distribution

### 2.3 Notebook 3: Model Training

#### [NEW] `notebooks/03_model_training.ipynb`

**Nội dung:**

1. **Load data từ MongoDB**
2. **Train/Test split** (80/20)
3. **Train 4 mô hình**:
    - Content-Based Filtering
    - Item-Based Collaborative Filtering
    - User-Based Collaborative Filtering
    - Hybrid Model
4. **Lưu trained models** (pickle files)

```python
# Train và save models
import pickle

# Content-Based
content_model = ContentBasedModel()
content_model.fit(movies_df)
with open('models/content_based.pkl', 'wb') as f:
    pickle.dump(content_model, f)
```

### 2.4 Notebook 4: Model Evaluation & Save to MongoDB

#### [NEW] `notebooks/04_model_evaluation.ipynb`

**Nội dung:**

1. **Load trained models**
2. **Đánh giá trên test set**:
    - RMSE
    - MAE
    - Precision@K (K=5, 10, 20)
    - Recall@K (K=5, 10, 20)
3. **So sánh các mô hình** (visualization)
4. **Lưu kết quả đánh giá lên MongoDB**

```python
# Đánh giá và lưu metrics lên MongoDB
from datetime import datetime

def evaluate_and_save(model, model_name, test_data, db):
    # Tính metrics
    predictions = model.predict(test_data)
    metrics = {
        'rmse': calculate_rmse(test_data['rating'], predictions),
        'mae': calculate_mae(test_data['rating'], predictions),
        'precision_at_5': precision_at_k(model, test_data, k=5),
        'precision_at_10': precision_at_k(model, test_data, k=10),
        'recall_at_5': recall_at_k(model, test_data, k=5),
        'recall_at_10': recall_at_k(model, test_data, k=10)
    }

    # Lưu lên MongoDB
    db.models.update_one(
        {'modelName': model_name},
        {
            '$set': {
                'modelName': model_name,
                'version': '1.0',
                'metrics': metrics,
                'trainedAt': datetime.now(),
                'isActive': True
            }
        },
        upsert=True
    )
    return metrics

# Evaluate all models
for model, name in [(content_model, 'content_based'),
                     (item_model, 'item_based'),
                     (user_model, 'user_based'),
                     (hybrid_model, 'hybrid')]:
    metrics = evaluate_and_save(model, name, test_df, db)
    print(f"{name}: {metrics}")
```

### 2.5 MongoDB Helper

#### [NEW] `notebooks/utils/mongo_helper.py`

```python
from pymongo import MongoClient
import pickle

class MongoHelper:
    def __init__(self, uri='mongodb://localhost:27017', db_name='movie_recommendation'):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def save_model_metrics(self, model_name, metrics, version='1.0'):
        """Lưu metrics của model lên MongoDB"""
        pass

    def get_model_metrics(self, model_name):
        """Lấy metrics của model từ MongoDB"""
        pass

    def save_similarity_matrix(self, model_name, matrix):
        """Lưu similarity matrix (pickled) lên MongoDB"""
        pass

    def load_similarity_matrix(self, model_name):
        """Load similarity matrix từ MongoDB"""
        pass
```

---

## 3. Thu thập Dữ liệu

### 3.1 Thu thập dữ liệu

#### [NEW] `scripts/download_data.py`

-   Download dataset từ Kaggle sử dụng `kagglehub`
-   Dataset: `parasharmanas/movie-recommendation-system`
-   Lưu vào thư mục `data/raw/`

### 3.2 Làm sạch dữ liệu (trong Notebook)

#### [NEW] `app/services/data_processing.py`

```python
class DataProcessor:
    def load_data() -> tuple[pd.DataFrame, pd.DataFrame]
    def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame
    def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame
    def handle_outliers(df: pd.DataFrame) -> pd.DataFrame
    def normalize_data(df: pd.DataFrame) -> pd.DataFrame
    def merge_datasets() -> pd.DataFrame
```

**Chi tiết xử lý:**

-   **Missing values**: Xóa hoặc fill với giá trị mặc định
-   **Duplicates**: Loại bỏ rating trùng lặp (giữ lại rating mới nhất)
-   **Outliers**: Rating ngoài khoảng [0.5, 5.0] sẽ được clip
-   **Normalize**: Chuẩn hóa rating về thang [0, 1]

---

## 4. Vector hóa & Feature Engineering

#### [NEW] `app/services/vectorization.py`

```python
class Vectorizer:
    def tfidf_vectorize(genres: pd.Series) -> sparse_matrix
    def create_embeddings(texts: list[str]) -> np.ndarray
    def create_user_item_matrix(ratings: pd.DataFrame) -> sparse_matrix
```

**Phương pháp:**

-   **TF-IDF**: Cho genres của phim
-   **Embeddings**: Sử dụng sentence-transformers cho title + genres
-   **User-Item Matrix**: Ma trận thưa cho collaborative filtering

---

## 5. Xây dựng 4 Mô hình Recommendation

### 4.1 Content-Based Filtering

#### [NEW] `app/models/content_based.py`

```python
class ContentBasedModel:
    def __init__(self)
    def fit(movies_df: pd.DataFrame)
    def get_similar_movies(movie_id: int, n: int = 10) -> list[dict]
    def recommend_for_user(user_id: int, n: int = 10) -> list[dict]
```

**Thuật toán:**

-   Sử dụng cosine similarity trên TF-IDF vectors của genres
-   Kết hợp với title embeddings để tăng độ chính xác

### 4.2 Item-Based Collaborative Filtering

#### [NEW] `app/models/item_based.py`

```python
class ItemBasedModel:
    def __init__(self)
    def fit(ratings_df: pd.DataFrame)
    def compute_item_similarity() -> np.ndarray
    def predict_rating(user_id: int, movie_id: int) -> float
    def recommend(user_id: int, n: int = 10) -> list[dict]
```

**Thuật toán:**

-   Tính similarity giữa các items dựa trên rating patterns
-   Sử dụng cosine similarity hoặc Pearson correlation

### 4.3 User-Based Collaborative Filtering

#### [NEW] `app/models/user_based.py`

```python
class UserBasedModel:
    def __init__(self)
    def fit(ratings_df: pd.DataFrame)
    def compute_user_similarity() -> np.ndarray
    def predict_rating(user_id: int, movie_id: int) -> float
    def recommend(user_id: int, n: int = 10) -> list[dict]
```

**Thuật toán:**

-   Tìm k users tương tự nhất
-   Dự đoán rating dựa trên weighted average của similar users

### 4.4 Hybrid Model

#### [NEW] `app/models/hybrid.py`

```python
class HybridModel:
    def __init__(self, models: list, weights: list[float])
    def fit(movies_df: pd.DataFrame, ratings_df: pd.DataFrame)
    def recommend(user_id: int, n: int = 10) -> list[dict]
    def explain_recommendation(movie_id: int) -> dict
```

**Thuật toán:**

-   Kết hợp predictions từ content-based và collaborative filtering
-   Weighted ensemble với configurable weights

---

## 6. API Endpoints

#### [NEW] `app/routes/recommendation.py`

| Method | Endpoint                         | Mô tả                   |
| ------ | -------------------------------- | ----------------------- |
| GET    | `/api/recommendations/<user_id>` | Gợi ý phim cho user     |
| GET    | `/api/similar/<movie_id>`        | Phim tương tự           |
| GET    | `/api/movies`                    | Danh sách phim          |
| GET    | `/api/movies/<movie_id>`         | Chi tiết phim           |
| POST   | `/api/ratings`                   | Thêm rating mới         |
| GET    | `/api/users/<user_id>/history`   | Lịch sử rating của user |

#### [NEW] `app/routes/analytics.py`

| Method | Endpoint                             | Mô tả           |
| ------ | ------------------------------------ | --------------- |
| GET    | `/api/analytics/rating-distribution` | Phân bố rating  |
| GET    | `/api/analytics/top-movies`          | Top phim        |
| GET    | `/api/analytics/genre-frequency`     | Tần suất genres |

---

## 7. Đánh giá Mô hình

#### [NEW] `app/services/evaluation.py`

```python
class ModelEvaluator:
    def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float
    def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float
    def precision_at_k(recommendations: list, relevant: list, k: int) -> float
    def recall_at_k(recommendations: list, relevant: list, k: int) -> float
    def evaluate_model(model, test_data: pd.DataFrame) -> dict
    def cross_validate(model, data: pd.DataFrame, k_folds: int = 5) -> dict
```

---

## 8. MongoDB Database

### 7.1 Connection Setup

#### [NEW] `app/database/connection.py`

```python
from pymongo import MongoClient
from pymongo.database import Database

class MongoDB:
    client: MongoClient = None
    db: Database = None

    @classmethod
    def connect(cls, uri: str, db_name: str):
        cls.client = MongoClient(uri)
        cls.db = cls.client[db_name]

    @classmethod
    def get_collection(cls, name: str):
        return cls.db[name]

    @classmethod
    def close(cls):
        cls.client.close()
```

### 7.2 Collections Schema

#### [NEW] `app/database/schemas.py`

**Collection: `movies`**

```json
{
    "_id": ObjectId,
    "movieId": int,
    "title": str,
    "genres": [str],
    "year": int,
    "avgRating": float,
    "ratingCount": int,
    "tfidfVector": [float],      // TF-IDF vector cho genres
    "embedding": [float],         // Sentence embedding
    "createdAt": datetime,
    "updatedAt": datetime
}
```

**Collection: `users`**

```json
{
    "_id": ObjectId,
    "userId": int,
    "username": str,
    "ratedMovies": [int],        // List movieIds đã rate
    "preferences": {
        "favoriteGenres": [str],
        "avgRating": float
    },
    "createdAt": datetime,
    "updatedAt": datetime
}
```

**Collection: `ratings`**

```json
{
    "_id": ObjectId,
    "userId": int,
    "movieId": int,
    "rating": float,
    "timestamp": datetime,
    "createdAt": datetime
}
```

**Collection: `models`** (Lưu trained models)

```json
{
    "_id": ObjectId,
    "modelName": str,            // "content_based", "item_based", etc.
    "version": str,
    "metrics": {
        "rmse": float,
        "mae": float,
        "precision_at_10": float,
        "recall_at_10": float
    },
    "parameters": dict,          // Model hyperparameters
    "similarityMatrix": Binary,  // Pickled numpy array
    "trainedAt": datetime,
    "isActive": bool
}
```

### 7.3 Indexes

```javascript
// Movies
db.movies.createIndex({ movieId: 1 }, { unique: true });
db.movies.createIndex({ genres: 1 });
db.movies.createIndex({ avgRating: -1 });

// Users
db.users.createIndex({ userId: 1 }, { unique: true });

// Ratings
db.ratings.createIndex({ userId: 1, movieId: 1 }, { unique: true });
db.ratings.createIndex({ movieId: 1 });
db.ratings.createIndex({ timestamp: -1 });

// Models
db.models.createIndex({ modelName: 1, version: 1 }, { unique: true });
```

### 7.4 Docker Compose

#### [NEW] `docker-compose.yml`

```yaml
version: "3.8"
services:
    mongodb:
        image: mongo:7.0
        container_name: movie_recommendation_db
        ports:
            - "27017:27017"
        volumes:
            - mongodb_data:/data/db
        environment:
            MONGO_INITDB_ROOT_USERNAME: admin
            MONGO_INITDB_ROOT_PASSWORD: password123
            MONGO_INITDB_DATABASE: movie_recommendation

volumes:
    mongodb_data:
```

---

## 9. Dependencies

#### [NEW] `requirements.txt`

```
flask>=2.0.0
flask-cors>=3.0.0
pandas>=1.3.0
numpy>=1.21.0
scikit-learn>=0.24.0
scipy>=1.7.0
sentence-transformers>=2.2.0
kagglehub>=0.1.0
python-dotenv>=0.19.0
gunicorn>=20.1.0
pymongo>=4.6.0
motor>=3.3.0
```

---

## 10. Verification Plan

### 9.1 MongoDB Testing

```bash
# Start MongoDB
docker-compose up -d

# Verify connection
python -c "from app.database.connection import MongoDB; MongoDB.connect('mongodb://localhost:27017', 'movie_recommendation'); print('Connected!')"
```

### 9.2 Unit Tests

```bash
# Chạy tất cả tests
pytest tests/ -v

# Test specific model
pytest tests/test_models.py::test_content_based -v
```

### 9.3 API Testing

```bash
# Test endpoint recommendations
curl http://localhost:5000/api/recommendations/1

# Test endpoint similar movies
curl http://localhost:5000/api/similar/1
```

### 9.4 Model Evaluation

```bash
# Chạy evaluation script
python -m app.services.evaluation --model all
```

**Metrics mong đợi:**

-   RMSE < 1.0
-   MAE < 0.8
-   Precision@10 > 0.3
-   Recall@10 > 0.2
