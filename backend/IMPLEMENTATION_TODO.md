# 📋 Backend Implementation TODO

> **Trạng thái**: Cập nhật lần cuối: 17/12/2025
> **Dự án**: Hệ thống Recommendation Phim

---

## 📊 Tổng quan tiến độ

| Hạng mục | Trạng thái | Ghi chú |
|----------|------------|---------|
| Thu thập dữ liệu | ✅ Hoàn thành | Script download từ Kaggle |
| Làm sạch dữ liệu | ✅ Hoàn thành | `data_processing.py` |
| Vector hóa | ✅ Hoàn thành | TF-IDF trong `vectorization.py` |
| 4 Mô hình Recommendation | ✅ Code hoàn thành | Chưa train |
| API Routes | ✅ Hoàn thành | movies, users, recommendations, analytics |
| MongoDB Connection | ✅ Hoàn thành | Connection & schemas |
| Jupyter Notebooks | ❌ Chưa có | Cần tạo 4 notebooks |
| Model Training | ❌ Chưa thực hiện | Cần train và lưu .pkl |
| Model Evaluation | ❌ Chưa thực hiện | Cần lưu metrics vào MongoDB |
| Context-aware Recommendation | ❌ Chưa có | Yêu cầu nâng cao |

---

## 🔴 VIỆC CẦN LÀM NGAY

### 1. Tạo Jupyter Notebooks (Ưu tiên cao)

#### 📓 Notebook 1: Data Preparation
**File**: `notebooks/01_data_preparation.ipynb`

**Nội dung cần có**:
- [ ] Load CSV files (movies.csv, ratings.csv)
- [ ] Kiểm tra thông tin dataset (shape, dtypes, info)
- [ ] Xử lý missing values
- [ ] Loại bỏ duplicates
- [ ] Xử lý outliers (ratings ngoài khoảng 0.5-5.0)
- [ ] Feature engineering:
  - [ ] Parse genres thành list
  - [ ] Extract year từ title
- [ ] Vector hóa với TF-IDF
- [ ] Import dữ liệu vào MongoDB
- [ ] Verify data trong MongoDB

---

#### 📓 Notebook 2: Data Exploration & Visualization
**File**: `notebooks/02_data_exploration.ipynb`

**Nội dung cần có**:
- [ ] Thống kê tổng quan (số movies, users, ratings)
- [ ] Phân bố rating (histogram)
- [ ] Top 10 genres phổ biến (bar chart)
- [ ] Top 20 movies theo rating count
- [ ] Top 20 movies theo average rating
- [ ] Rating heatmap (user x movie sample)
- [ ] Phân bố số ratings theo user
- [ ] Phân bố năm phát hành phim
- [ ] Correlation analysis

**Thư viện cần dùng**: matplotlib, seaborn, plotly

---

#### 📓 Notebook 3: Model Training
**File**: `notebooks/03_model_training.ipynb`

**Nội dung cần có**:
- [ ] Load data từ MongoDB
- [ ] Train/Test split (80/20)
- [ ] **Train Content-Based Model**:
  - [ ] TF-IDF vectorization
  - [ ] Cosine similarity matrix
  - [ ] Save model to `models_saved/content_based.pkl`
- [ ] **Train Item-Based Collaborative Filtering**:
  - [ ] Item-item similarity matrix
  - [ ] Save model to `models_saved/item_based.pkl`
- [ ] **Train User-Based Collaborative Filtering**:
  - [ ] User-user similarity matrix
  - [ ] Save model to `models_saved/user_based.pkl`
- [ ] **Train Hybrid Model**:
  - [ ] Combine 3 models với weights
  - [ ] Save model to `models_saved/hybrid.pkl`
- [ ] Test predictions cho sample users

---

#### 📓 Notebook 4: Model Evaluation
**File**: `notebooks/04_model_evaluation.ipynb`

**Nội dung cần có**:
- [ ] Load trained models
- [ ] Load test data
- [ ] **Tính metrics cho mỗi model**:
  - [ ] RMSE (Root Mean Square Error)
  - [ ] MAE (Mean Absolute Error)
  - [ ] Precision@K (K = 5, 10, 20)
  - [ ] Recall@K (K = 5, 10, 20)
  - [ ] F1@K
  - [ ] NDCG@K
  - [ ] Coverage
- [ ] So sánh hiệu suất các models (bảng + biểu đồ)
- [ ] **Lưu metrics vào MongoDB** collection `model_metrics`
- [ ] Kết luận và recommendations

---

### 2. Train và Lưu Models

**Thư mục output**: `models_saved/`

| Model | File | Trạng thái |
|-------|------|------------|
| Content-Based | `content_based.pkl` | ❌ Chưa có |
| Item-Based | `item_based.pkl` | ❌ Chưa có |
| User-Based | `user_based.pkl` | ❌ Chưa có |
| Hybrid | `hybrid.pkl` | ❌ Chưa có |

---

### 3. MongoDB Collections cần có

| Collection | Trạng thái | Ghi chú |
|------------|------------|---------|
| `movies` | ✅ Schema có | Cần import data |
| `users` | ✅ Schema có | Cần import data |
| `ratings` | ✅ Schema có | Cần import data |
| `model_metrics` | ❌ Chưa có | Cần tạo để lưu evaluation results |

**Schema cho `model_metrics`**:
```javascript
{
  modelName: String,       // "content_based", "item_based", etc.
  version: String,         // "1.0.0"
  trainedAt: Date,
  metrics: {
    rmse: Number,
    mae: Number,
    precision_at_5: Number,
    precision_at_10: Number,
    precision_at_20: Number,
    recall_at_5: Number,
    recall_at_10: Number,
    recall_at_20: Number,
    f1_at_10: Number,
    ndcg_at_10: Number,
    coverage: Number
  },
  trainSize: Number,
  testSize: Number,
  parameters: Object       // Model hyperparameters
}
```

---

## 🟡 VIỆC CẦN LÀM SAU

### 4. Yêu cầu nâng cao (Optional)

- [ ] **Embeddings nâng cao**: Sử dụng Word2Vec hoặc BERT cho title/genres
- [ ] **Context-aware recommendation**: 
  - [ ] Thêm time-based features
  - [ ] Trending movies
  - [ ] Seasonal recommendations
- [ ] **Real-time updates**: 
  - [ ] Cập nhật model khi có rating mới
  - [ ] Incremental learning

---

## 🛠️ Hướng dẫn thực hiện

### Bước 1: Chuẩn bị môi trường
```bash
cd backend
pip install -r requirements.txt
pip install jupyter matplotlib seaborn plotly tqdm
```

### Bước 2: Download dữ liệu
```bash
python scripts/download_data.py
```

### Bước 3: Khởi động MongoDB
```bash
docker-compose up -d
```

### Bước 4: Import dữ liệu (nếu chưa có notebooks)
```bash
python scripts/import_to_mongodb.py
```

### Bước 5: Chạy Jupyter Notebooks theo thứ tự
```bash
cd notebooks
jupyter notebook
```
Thực hiện theo thứ tự: 01 → 02 → 03 → 04

### Bước 6: Verify models
```bash
ls models_saved/
# Phải có: content_based.pkl, item_based.pkl, user_based.pkl, hybrid.pkl
```

### Bước 7: Test API
```bash
python run.py
# Test: http://localhost:5000/api/recommendations/1
```

---

## 📁 Cấu trúc thư mục hoàn chỉnh

```
backend/
├── app/                      ✅ Hoàn thành
├── data/
│   ├── raw/                  ✅ movies.csv, ratings.csv
│   └── processed/            ⏳ Sẽ tạo từ notebooks
├── models_saved/             ❌ Cần tạo .pkl files
│   ├── content_based.pkl
│   ├── item_based.pkl
│   ├── user_based.pkl
│   └── hybrid.pkl
├── notebooks/                ❌ Cần tạo
│   ├── 01_data_preparation.ipynb
│   ├── 02_data_exploration.ipynb
│   ├── 03_model_training.ipynb
│   ├── 04_model_evaluation.ipynb
│   └── utils/
│       └── mongo_helper.py   ✅ Có
├── scripts/                  ✅ Hoàn thành
├── docker-compose.yml        ✅ Có
├── requirements.txt          ✅ Có
└── run.py                    ✅ Có
```

---

## ⏰ Ước tính thời gian

| Task | Thời gian ước tính |
|------|-------------------|
| Notebook 1: Data Preparation | 1-2 giờ |
| Notebook 2: Data Exploration | 2-3 giờ |
| Notebook 3: Model Training | 3-4 giờ |
| Notebook 4: Model Evaluation | 2-3 giờ |
| Testing & Debugging | 2-3 giờ |
| **Tổng cộng** | **10-15 giờ** |

---

## 📝 Ghi chú

1. **Ưu tiên Notebook 1 và 3** vì đây là core functionality
2. **Có thể dùng script thay notebooks** nếu cần nhanh, nhưng notebooks giúp documentation tốt hơn
3. **Test từng bước** - sau mỗi notebook, verify kết quả trước khi tiếp tục
4. **Backup MongoDB** trước khi chạy lại import

---

> 💡 **Tip**: Bắt đầu với dataset nhỏ (limit ratings) để test nhanh, sau đó chạy full dataset.
