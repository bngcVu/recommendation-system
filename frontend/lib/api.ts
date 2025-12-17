/**
 * API client for connecting to backend recommendation service.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api';

// Types matching backend responses
export interface Movie {
    movieId: number;
    title: string;
    genres: string[];
    avgRating: number;
    ratingCount: number;
    year?: number;
    score?: number;
    similarity?: number;
    method?: string;
}

export interface User {
    userId: number;
    username: string;
    ratedMovies: number[];
    watchedMovies: number[];
    preferences?: {
        favoriteGenres?: string[];
        avgRating?: number;
    };
}

export interface Rating {
    movieId: number;
    userId: number;
    rating: number;
    timestamp?: string;
}

export interface RatingHistoryItem {
    movieId: number;
    title: string;
    genres: string[];
    userRating: number;
    timestamp: string;
    avgRating?: number;
}

export interface Analytics {
    totalMovies: number;
    totalUsers: number;
    totalRatings: number;
    avgRating: number;
}

export interface RatingDistribution {
    rating: number;
    count: number;
}

export interface GenreFrequency {
    genre: string;
    count: number;
}

export interface ModelMetrics {
    modelName: string;
    version: string;
    metrics: {
        rmse?: number;
        mae?: number;
        'precision@10'?: number;
        'recall@10'?: number;
    };
    trainedAt?: string;
    isActive?: boolean;
}

export interface Recommendation extends Movie {
    score: number;
    method: string;
    component_scores?: Record<string, number>;
}

// API Error handling
class ApiError extends Error {
    constructor(public status: number, message: string) {
        super(message);
        this.name = 'ApiError';
    }
}

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options?.headers,
            },
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
            throw new ApiError(response.status, errorData.error || 'Request failed');
        }

        return response.json();
    } catch (error) {
        if (error instanceof ApiError) throw error;
        console.error('API Error:', error);
        throw new ApiError(500, 'Failed to connect to server');
    }
}

// ============= Movies API =============

export async function getMovies(params?: {
    page?: number;
    limit?: number;
    genre?: string;
    sort?: string;
    order?: 'asc' | 'desc';
    search?: string;
}): Promise<{ movies: Movie[]; page: number; limit: number; total: number; pages: number }> {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.set('page', String(params.page));
    if (params?.limit) searchParams.set('limit', String(params.limit));
    if (params?.genre) searchParams.set('genre', params.genre);
    if (params?.sort) searchParams.set('sort', params.sort);
    if (params?.order) searchParams.set('order', params.order);
    if (params?.search) searchParams.set('search', params.search);

    return fetchApi(`/movies?${searchParams.toString()}`);
}

export async function getMovie(movieId: number): Promise<Movie> {
    return fetchApi(`/movies/${movieId}`);
}

export async function getMoviesByGenre(
    genre: string,
    params?: { page?: number; limit?: number }
): Promise<{ movies: Movie[]; genre: string; page: number; limit: number; total: number }> {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.set('page', String(params.page));
    if (params?.limit) searchParams.set('limit', String(params.limit));

    return fetchApi(`/movies/genre/${encodeURIComponent(genre)}?${searchParams.toString()}`);
}

export async function getTopMovies(limit: number = 10): Promise<{ movies: Movie[] }> {
    return fetchApi(`/movies/top?limit=${limit}`);
}

export async function searchMovies(query: string, limit: number = 20): Promise<{ movies: Movie[]; query: string }> {
    return fetchApi(`/movies/search?q=${encodeURIComponent(query)}&limit=${limit}`);
}

export async function getGenres(): Promise<{ genres: string[] }> {
    return fetchApi('/genres');
}

// ============= Users API =============

export async function getUser(userId: number): Promise<User> {
    return fetchApi(`/users/${userId}`);
}

export async function getUserHistory(
    userId: number,
    limit: number = 50
): Promise<{ userId: number; history: RatingHistoryItem[] }> {
    return fetchApi(`/users/${userId}/history?limit=${limit}`);
}

export async function addRating(userId: number, movieId: number, rating: number): Promise<{ message: string }> {
    return fetchApi('/ratings', {
        method: 'POST',
        body: JSON.stringify({ userId, movieId, rating }),
    });
}

export async function getRating(userId: number, movieId: number): Promise<{ rating: number | null }> {
    return fetchApi(`/ratings/${userId}/${movieId}`);
}

export async function recordWatch(userId: number, movieId: number): Promise<{ message: string }> {
    return fetchApi(`/users/${userId}/watch`, {
        method: 'POST',
        body: JSON.stringify({ movieId }),
    });
}

// ============= Recommendations API =============

export async function getRecommendations(
    userId: number,
    params?: { model?: string; n?: number }
): Promise<{ userId: number; model: string; recommendations: Recommendation[] }> {
    const searchParams = new URLSearchParams();
    if (params?.model) searchParams.set('model', params.model);
    if (params?.n) searchParams.set('n', String(params.n));

    return fetchApi(`/recommendations/${userId}?${searchParams.toString()}`);
}

export async function getSimilarMovies(
    movieId: number,
    params?: { model?: string; n?: number }
): Promise<{ movieId: number; model: string; similar: Movie[] }> {
    const searchParams = new URLSearchParams();
    if (params?.model) searchParams.set('model', params.model);
    if (params?.n) searchParams.set('n', String(params.n));

    return fetchApi(`/similar/${movieId}?${searchParams.toString()}`);
}

export async function getModels(): Promise<{ models: ModelMetrics[] }> {
    return fetchApi('/models');
}

export async function compareModels(): Promise<{
    comparison: { metrics: string[]; models: ModelMetrics[] };
}> {
    return fetchApi('/models/compare');
}

// ============= Analytics API =============

export async function getStats(): Promise<Analytics> {
    return fetchApi('/analytics/stats');
}

export async function getRatingDistribution(): Promise<{ distribution: RatingDistribution[] }> {
    return fetchApi('/analytics/rating-distribution');
}

export async function getTopMoviesAnalytics(
    limit: number = 10,
    minRatings: number = 50
): Promise<{ movies: Movie[] }> {
    return fetchApi(`/analytics/top-movies?limit=${limit}&min_ratings=${minRatings}`);
}

export async function getGenreFrequency(): Promise<{ genres: GenreFrequency[] }> {
    return fetchApi('/analytics/genre-frequency');
}

export async function getHeatmapData(
    nUsers: number = 20,
    nMovies: number = 20
): Promise<{ userIds: number[]; movieIds: number[]; matrix: Record<number, Record<number, number>> }> {
    return fetchApi(`/analytics/heatmap?n_users=${nUsers}&n_movies=${nMovies}`);
}

// ============= Health Check =============

export async function healthCheck(): Promise<{ status: string; database: string }> {
    try {
        const response = await fetch(`${API_BASE_URL.replace('/api', '')}/health`);
        return response.json();
    } catch {
        return { status: 'error', database: 'disconnected' };
    }
}
