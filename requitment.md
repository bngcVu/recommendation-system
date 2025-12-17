# I. MÔ TẢ BÀI TOÁN

Bạn được giao nhiệm vụ xây dựng một hệ thống recommendation cho một nền tảng: Gợi ý phim

Hệ thống cần có khả năng:
1. Thu thập dữ liệu
2. Làm sạch dữ liệu
3. Trực quan hóa dữ liệu
4. Xây dựng mô hình recommendation
5. Hiển thị gợi ý cho người dùng

Mô tả dataset: 
Download từ: kagglehub hoặc curl

import kagglehub

# Download latest version
path = kagglehub.dataset_download("parasharmanas/movie-recommendation-system")

print("Path to dataset files:", path)

#!/bin/bash
curl -L -o ~/Downloads/movie-recommendation-system.zip\
  https://www.kaggle.com/api/v1/datasets/download/parasharmanas/movie-recommendation-system

Dataset bao gồm:
- movies.csv: movieId, title, genres
- ratings.csv: userId, movieId, rating, timestamp

# II. YÊU CẦU & NHIỆM VỤ CHI TIẾT

## 1. Thu thập dữ liệu
- Dataset ≥ 2.000 items
- Có ít nhất 5 features mô tả item

## 2. Làm sạch và chuẩn bị dữ liệu
- Missing values
- Chuẩn hóa dữ liệu
- Loại bỏ duplicate
- Xử lý outlier
- Vector hóa (TF-IDF, BOW, embeddings)

## 3. Phân tích & trực quan hóa dữ liệu
- Phân bố rating
- Tần suất nhóm sản phẩm
- Top items
- Heatmap, bar chart, histogram

## 4. Xây dựng hệ thống gợi ý
- 4 module gợi ý bao gồm: content-based, item-based, user-based, hybrid
## 5. Đánh giá mô hình
- RMSE, MAE, Precision@K, Recall@K

## 6. Giao diện hiển thị
Có thể sử dụng AI để tạo:
- Web interface (Flask)

## 7. Yêu cầu thêm
- Sử dụng embeddings nâng cao
- Gợi ý theo thời gian thực
- Lưu lịch sử người dùng
- Context-aware recommendation
