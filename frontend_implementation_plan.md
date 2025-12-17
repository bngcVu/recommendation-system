# Frontend Implementation Plan - Hệ Thống Recommendation Phim

## Tổng quan

Xây dựng giao diện web cho hệ thống gợi ý phim, hiển thị trực quan hóa dữ liệu, gợi ý phim và cho phép người dùng tương tác với hệ thống.

---

## 1. Cấu trúc thư mục Frontend

```
frontend/
├── static/
│   ├── css/
│   │   ├── main.css           # Styles chính
│   │   ├── components.css     # Component styles
│   │   └── charts.css         # Chart styles
│   └── js/
│       ├── app.js             # Main application logic
│       ├── api.js             # API calls
│       ├── charts.js          # Chart rendering
│       └── components.js      # UI components
├── templates/
│   ├── base.html              # Base template
│   ├── index.html             # Trang chủ
│   ├── movies.html            # Danh sách phim
│   ├── movie_detail.html      # Chi tiết phim
│   ├── recommendations.html   # Trang gợi ý
│   └── analytics.html         # Trang phân tích
└── README.md
```

---

## 2. Các Trang Giao Diện

### 2.1 Trang Chủ (Home)

#### [NEW] `templates/index.html`

**Thành phần:**

-   Hero section với search bar
-   Top phim được đánh giá cao
-   Phim mới nhất
-   Quick recommendation preview

**Layout:**

```
┌─────────────────────────────────────────────┐
│              HEADER / NAVIGATION            │
├─────────────────────────────────────────────┤
│                                             │
│              HERO SECTION                   │
│         "Khám phá phim yêu thích"           │
│            [   Search Bar   ]               │
│                                             │
├─────────────────────────────────────────────┤
│  TOP RATED MOVIES (Carousel)                │
│  [Card][Card][Card][Card][Card]             │
├─────────────────────────────────────────────┤
│  RECOMMENDED FOR YOU                        │
│  [Card][Card][Card][Card]                   │
├─────────────────────────────────────────────┤
│              FOOTER                         │
└─────────────────────────────────────────────┘
```

### 2.2 Trang Gợi Ý (Recommendations)

#### [NEW] `templates/recommendations.html`

**Thành phần:**

-   User selector/login
-   Gợi ý từ 4 mô hình với tabs
-   Filter theo genres
-   Lịch sử xem của user

**Layout:**

```
┌─────────────────────────────────────────────┐
│              HEADER / NAVIGATION            │
├─────────────────────────────────────────────┤
│  User: [Select User ▼]   [Genres Filter ▼] │
├─────────────────────────────────────────────┤
│  TABS: [Content] [Item-Based] [User-Based] [Hybrid]
├─────────────────────────────────────────────┤
│                                             │
│  RECOMMENDATION RESULTS                     │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐           │
│  │Movie│ │Movie│ │Movie│ │Movie│           │
│  │Card │ │Card │ │Card │ │Card │           │
│  └─────┘ └─────┘ └─────┘ └─────┘           │
│                                             │
├─────────────────────────────────────────────┤
│  YOUR RATING HISTORY                        │
│  [Rated Movie 1] [Rated Movie 2] ...        │
└─────────────────────────────────────────────┘
```

### 2.3 Trang Chi Tiết Phim

#### [NEW] `templates/movie_detail.html`

**Thành phần:**

-   Thông tin phim (title, genres, avg rating)
-   Rating input
-   Phim tương tự
-   User reviews

### 2.4 Trang Phân Tích Dữ Liệu (Analytics)

#### [NEW] `templates/analytics.html`

**Thành phần:**

-   **Phân bố Rating**: Histogram
-   **Top Genres**: Bar chart
-   **Top Movies**: Horizontal bar chart
-   **Rating Heatmap**: Matrix heatmap
-   **Statistics Summary**: Cards với key metrics

**Layout:**

```
┌─────────────────────────────────────────────┐
│              HEADER / NAVIGATION            │
├─────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐         │
│  │  Total Movies│  │  Total Users │         │
│  │    10,000    │  │    50,000    │         │
│  └──────────────┘  └──────────────┘         │
│  ┌──────────────┐  ┌──────────────┐         │
│  │ Total Ratings│  │  Avg Rating  │         │
│  │  1,000,000   │  │     3.5      │         │
│  └──────────────┘  └──────────────┘         │
├─────────────────────────────────────────────┤
│  RATING DISTRIBUTION    │  TOP GENRES       │
│  ┌──────────────────┐   │  ┌─────────────┐  │
│  │   [Histogram]    │   │  │ [Bar Chart] │  │
│  └──────────────────┘   │  └─────────────┘  │
├─────────────────────────────────────────────┤
│  TOP RATED MOVIES       │  RATING HEATMAP   │
│  ┌──────────────────┐   │  ┌─────────────┐  │
│  │  [Horizontal Bar]│   │  │  [Heatmap]  │  │
│  └──────────────────┘   │  └─────────────┘  │
└─────────────────────────────────────────────┘
```

---

## 3. Components

### 3.1 Movie Card Component

#### [NEW] `static/js/components.js`

```javascript
class MovieCard {
    constructor(movie) // movie: {id, title, genres, avgRating}
    render() // Returns HTML string
    addEventListeners()
    generateGradient(title) // Tạo gradient dựa trên hash của title
}
```

**Design:**

> [!NOTE]
> Dataset không có ảnh phim, sử dụng **gradient background + title text** thay thế.

-   **Gradient placeholder** với màu được tạo từ hash của title phim
-   Title hiển thị lớn ở giữa card
-   Genres tags ở dưới
-   Star rating display
-   Hover effect với scale và shadow

**Gradient Generation:**

```javascript
// Tạo màu gradient từ title để mỗi phim có màu khác nhau
function generateGradient(title) {
    const hash = title.split("").reduce((a, b) => (a << 5) - a + b.charCodeAt(0), 0);
    const hue1 = Math.abs(hash) % 360;
    const hue2 = (hue1 + 40) % 360;
    return `linear-gradient(135deg, hsl(${hue1}, 70%, 30%), hsl(${hue2}, 70%, 20%))`;
}
```

### 3.2 Rating Component

```javascript
class RatingInput {
    constructor(movieId, currentRating)
    render()
    onRatingChange(callback)
    submitRating()
}
```

**Design:**

-   5 star interactive input
-   Half-star support
-   Submit button
-   Loading state

### 3.3 Search Component

```javascript
class SearchBar {
    constructor(placeholder)
    render()
    onSearch(callback)
    showSuggestions(movies)
}
```

---

## 4. Charts & Trực quan hóa

#### [NEW] `static/js/charts.js`

Sử dụng **Chart.js** hoặc **D3.js** để vẽ charts.

```javascript
// Rating Distribution Histogram
function renderRatingHistogram(data, containerId)

// Genre Frequency Bar Chart
function renderGenreBarChart(data, containerId)

// Top Movies Horizontal Bar
function renderTopMoviesChart(data, containerId)

// Rating Heatmap (User x Movie sample)
function renderRatingHeatmap(data, containerId)
```

**Chart Types:**
| Chart | Library | Mô tả |
|-------|---------|-------|
| Histogram | Chart.js | Phân bố rating |
| Bar Chart | Chart.js | Tần suất genres |
| Horizontal Bar | Chart.js | Top movies |
| Heatmap | D3.js | Ma trận ratings |

---

## 5. API Integration

#### [NEW] `static/js/api.js`

```javascript
const API = {
    // Movies
    getMovies: (params) => fetch("/api/movies?" + params),
    getMovie: (id) => fetch(`/api/movies/${id}`),

    // Recommendations
    getRecommendations: (userId, model) => fetch(`/api/recommendations/${userId}?model=${model}`),
    getSimilarMovies: (movieId) => fetch(`/api/similar/${movieId}`),

    // Ratings
    submitRating: (userId, movieId, rating) =>
        fetch("/api/ratings", {
            method: "POST",
            body: JSON.stringify({ userId, movieId, rating }),
        }),
    getUserHistory: (userId) => fetch(`/api/users/${userId}/history`),

    // Analytics
    getRatingDistribution: () => fetch("/api/analytics/rating-distribution"),
    getTopMovies: () => fetch("/api/analytics/top-movies"),
    getGenreFrequency: () => fetch("/api/analytics/genre-frequency"),
};
```

---

## 6. Styling

#### [NEW] `static/css/main.css`

**Design System:**

-   **Colors**: White/Light theme với accent màu xanh dương (phong cách hiện đại, sạch sẽ)
-   **Typography**: Inter hoặc Roboto
-   **Spacing**: 8px grid system
-   **Border Radius**: 12px cho cards
-   **Shadows**: Subtle shadows cho depth

**Color Palette:**

```css
:root {
    /* Background */
    --bg-primary: #ffffff;
    --bg-secondary: #f5f5f7;
    --bg-card: #ffffff;

    /* Text */
    --text-primary: #1d1d1f;
    --text-secondary: #6e6e73;
    --text-muted: #86868b;

    /* Accent */
    --accent: #007aff;
    --accent-hover: #0056b3;
    --accent-secondary: #ff9500;

    /* Status */
    --success: #34c759;
    --warning: #ff9500;
    --error: #ff3b30;

    /* Borders & Shadows */
    --border-color: #e5e5e7;
    --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.08);
    --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.12);
}
```

---

## 7. Responsive Design

**Breakpoints:**

-   Mobile: < 768px
-   Tablet: 768px - 1024px
-   Desktop: > 1024px

**Mobile Adaptations:**

-   Movie cards: 2 per row → 1 per row
-   Navigation: Hamburger menu
-   Charts: Simplified/scrollable
-   Tabs: Horizontal scroll

---

## 8. Dependencies

```html
<!-- Chart.js for visualizations -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<!-- D3.js for heatmap -->
<script src="https://d3js.org/d3.v7.min.js"></script>

<!-- Google Fonts -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />

<!-- Font Awesome for icons -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" />
```

---

## 9. Verification Plan

### 9.1 Browser Testing

**Manual Testing Steps:**

1. Mở browser tại `http://localhost:5000`
2. Kiểm tra trang chủ load đúng với top movies
3. Click vào movie card → trang chi tiết hiển thị đúng
4. Chọn user → gợi ý phim xuất hiện
5. Chuyển tabs giữa các model → kết quả thay đổi
6. Submit rating → thấy confirmation message
7. Mở trang Analytics → các charts render đúng

### 9.2 Responsive Testing

```
1. Mở DevTools (F12)
2. Toggle device toolbar
3. Test với các kích thước: iPhone SE, iPad, Desktop
4. Verify layout không bị vỡ
```

### 9.3 Performance Check

```bash
# Lighthouse audit
npx lighthouse http://localhost:5000 --view
```

**Metrics mong đợi:**

-   Performance Score > 80
-   First Contentful Paint < 2s
-   Time to Interactive < 3s
