// Mock data for the movie recommendation system

export interface Movie {
  id: number
  title: string
  genres: string[]
  avgRating: number
  ratingCount: number
  year?: number
}

export interface User {
  id: number
  name: string
}

export interface Rating {
  movieId: number
  userId: number
  rating: number
  timestamp: string
}

// Generate gradient from title hash
export function generateGradient(title: string): string {
  const hash = title.split("").reduce((a, b) => ((a << 5) - a + b.charCodeAt(0)) | 0, 0)
  const hue1 = Math.abs(hash) % 360
  const hue2 = (hue1 + 40) % 360
  return `linear-gradient(135deg, hsl(${hue1}, 70%, 35%), hsl(${hue2}, 70%, 25%))`
}

// Mock movies data
export const mockMovies: Movie[] = [
  { id: 1, title: "The Shawshank Redemption", genres: ["Drama"], avgRating: 4.8, ratingCount: 12453, year: 1994 },
  { id: 2, title: "The Godfather", genres: ["Crime", "Drama"], avgRating: 4.7, ratingCount: 9821, year: 1972 },
  {
    id: 3,
    title: "The Dark Knight",
    genres: ["Action", "Crime", "Drama"],
    avgRating: 4.6,
    ratingCount: 15234,
    year: 2008,
  },
  { id: 4, title: "Pulp Fiction", genres: ["Crime", "Drama"], avgRating: 4.5, ratingCount: 8932, year: 1994 },
  { id: 5, title: "Forrest Gump", genres: ["Drama", "Romance"], avgRating: 4.5, ratingCount: 11234, year: 1994 },
  {
    id: 6,
    title: "Inception",
    genres: ["Action", "Sci-Fi", "Thriller"],
    avgRating: 4.4,
    ratingCount: 13456,
    year: 2010,
  },
  { id: 7, title: "The Matrix", genres: ["Action", "Sci-Fi"], avgRating: 4.4, ratingCount: 10234, year: 1999 },
  {
    id: 8,
    title: "Goodfellas",
    genres: ["Biography", "Crime", "Drama"],
    avgRating: 4.3,
    ratingCount: 7654,
    year: 1990,
  },
  {
    id: 9,
    title: "Interstellar",
    genres: ["Adventure", "Drama", "Sci-Fi"],
    avgRating: 4.3,
    ratingCount: 12876,
    year: 2014,
  },
  { id: 10, title: "Fight Club", genres: ["Drama"], avgRating: 4.3, ratingCount: 9876, year: 1999 },
  {
    id: 11,
    title: "The Lord of the Rings",
    genres: ["Adventure", "Drama", "Fantasy"],
    avgRating: 4.6,
    ratingCount: 14532,
    year: 2001,
  },
  {
    id: 12,
    title: "Star Wars",
    genres: ["Action", "Adventure", "Fantasy"],
    avgRating: 4.4,
    ratingCount: 11234,
    year: 1977,
  },
]

// Mock users
export const mockUsers: User[] = [
  { id: 1, name: "Nguyễn Văn A" },
  { id: 2, name: "Trần Thị B" },
  { id: 3, name: "Lê Văn C" },
  { id: 4, name: "Phạm Thị D" },
  { id: 5, name: "Hoàng Văn E" },
]

// Mock user rating history
export const mockUserHistory: Record<number, Rating[]> = {
  1: [
    { movieId: 1, userId: 1, rating: 5, timestamp: "2024-01-15" },
    { movieId: 3, userId: 1, rating: 4.5, timestamp: "2024-01-10" },
    { movieId: 6, userId: 1, rating: 4, timestamp: "2024-01-05" },
  ],
  2: [
    { movieId: 2, userId: 2, rating: 5, timestamp: "2024-01-14" },
    { movieId: 4, userId: 2, rating: 4, timestamp: "2024-01-12" },
    { movieId: 8, userId: 2, rating: 4.5, timestamp: "2024-01-08" },
  ],
}

// Mock analytics data
export const mockAnalytics = {
  totalMovies: 10000,
  totalUsers: 50000,
  totalRatings: 1000000,
  avgRating: 3.52,
  ratingDistribution: [
    { rating: 0.5, count: 5234 },
    { rating: 1, count: 12453 },
    { rating: 1.5, count: 18976 },
    { rating: 2, count: 45678 },
    { rating: 2.5, count: 78934 },
    { rating: 3, count: 156789 },
    { rating: 3.5, count: 234567 },
    { rating: 4, count: 289876 },
    { rating: 4.5, count: 123456 },
    { rating: 5, count: 34037 },
  ],
  topGenres: [
    { genre: "Drama", count: 4532 },
    { genre: "Comedy", count: 3421 },
    { genre: "Action", count: 2876 },
    { genre: "Thriller", count: 2345 },
    { genre: "Romance", count: 1987 },
    { genre: "Adventure", count: 1654 },
    { genre: "Sci-Fi", count: 1432 },
    { genre: "Horror", count: 1234 },
    { genre: "Crime", count: 1098 },
    { genre: "Fantasy", count: 876 },
  ],
}

// All available genres
export const allGenres = [
  "Action",
  "Adventure",
  "Animation",
  "Biography",
  "Comedy",
  "Crime",
  "Documentary",
  "Drama",
  "Family",
  "Fantasy",
  "Horror",
  "Musical",
  "Mystery",
  "Romance",
  "Sci-Fi",
  "Thriller",
  "War",
  "Western",
]
