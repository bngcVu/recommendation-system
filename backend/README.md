# Movie Recommendation System - Backend

Hệ thống gợi ý phim sử dụng Flask và MongoDB với 4 mô hình recommendation.

## Cấu trúc thư mục

```
backend/
├── app/
│   ├── __init__.py            # Flask app factory
│   ├── config.py              # Configuration settings
│   ├── database/              # MongoDB connection & schemas
│   ├── models/                # 4 recommendation models
│   ├── routes/                # API endpoints
│   ├── services/              # Business logic services
│   └── utils/                 # Helper utilities
├── data/
│   ├── raw/                   # Raw CSV data
│   └── processed/             # Processed data
├── models_saved/              # Saved trained models
├── notebooks/                 # Jupyter notebooks
├── scripts/                   # Utility scripts
├── requirements.txt
├── docker-compose.yml
└── run.py
```

## Cài đặt

1. **Tạo virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. **Cài đặt dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Khởi động MongoDB (Docker):**
   ```bash
   docker-compose up -d
   ```

4. **Download dataset:**
   ```bash
   python scripts/download_data.py
   ```

5. **Chạy server:**
   ```bash
   python run.py
   ```

## API Endpoints

### Movies
- `GET /api/movies` - Danh sách phim
- `GET /api/movies/<id>` - Chi tiết phim
- `GET /api/movies/genre/<genre>` - Phim theo thể loại
- `GET /api/movies/top` - Top phim
- `GET /api/movies/search?q=<query>` - Tìm kiếm phim
- `GET /api/genres` - Danh sách thể loại

### Users
- `GET /api/users` - Danh sách users
- `GET /api/users/<id>` - Chi tiết user
- `GET /api/users/<id>/history` - Lịch sử rating
- `POST /api/ratings` - Thêm rating mới
- `POST /api/users/<id>/watch` - Ghi nhận xem phim

### Recommendations
- `GET /api/recommendations/<user_id>?model=<model>` - Gợi ý phim
- `GET /api/similar/<movie_id>` - Phim tương tự
- `GET /api/models` - Danh sách models & metrics
- `GET /api/models/compare` - So sánh models

### Analytics
- `GET /api/analytics/stats` - Thống kê tổng quan
- `GET /api/analytics/rating-distribution` - Phân bố rating
- `GET /api/analytics/top-movies` - Top phim
- `GET /api/analytics/genre-frequency` - Tần suất thể loại
- `GET /api/analytics/heatmap` - Rating heatmap

## Models

1. **Content-Based Filtering** - TF-IDF trên genres
2. **Item-Based Collaborative Filtering** - Item similarity
3. **User-Based Collaborative Filtering** - User similarity  
4. **Hybrid Model** - Kết hợp 3 models trên

## Environment Variables

Tạo file `.env` từ `.env.example`:
```
SECRET_KEY=your-secret-key
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DB=movie_recommendation
```
