"use client"

import { useState, useEffect } from "react"
import { getMovie, getSimilarMovies, addRating, type Movie } from "@/lib/api"
import { MovieCard } from "@/components/movie-card"
import { RatingInput } from "@/components/rating-input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Star, Users, Calendar, TrendingUp, CheckCircle, Loader2 } from "lucide-react"
import { useAuth } from "@/contexts/auth-context"

// Generate gradient from title hash
function generateGradient(title: string): string {
    const hash = title.split("").reduce((a, b) => ((a << 5) - a + b.charCodeAt(0)) | 0, 0)
    const hue1 = Math.abs(hash) % 360
    const hue2 = (hue1 + 40) % 360
    return `linear-gradient(135deg, hsl(${hue1}, 70%, 35%), hsl(${hue2}, 70%, 25%))`
}

interface MovieDetailWrapperProps {
    movieId: number
}

export function MovieDetailWrapper({ movieId }: MovieDetailWrapperProps) {
    const { user } = useAuth()
    const [mounted, setMounted] = useState(false)
    const [movie, setMovie] = useState<Movie | null>(null)
    const [similarMovies, setSimilarMovies] = useState<Movie[]>([])
    const [isLoading, setIsLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [ratingSubmitted, setRatingSubmitted] = useState(false)

    useEffect(() => {
        setMounted(true)
    }, [])

    useEffect(() => {
        if (!mounted) return

        async function loadMovie() {
            setIsLoading(true)
            setError(null)
            try {
                const movieData = await getMovie(movieId)
                setMovie(movieData)

                // Load similar movies
                try {
                    const similarData = await getSimilarMovies(movieId, { model: 'content_based', n: 6 })
                    setSimilarMovies(similarData.similar)
                } catch {
                    console.error("Failed to load similar movies")
                }
            } catch (err) {
                console.error("Failed to load movie:", err)
                setError("Không thể tải thông tin phim")
            } finally {
                setIsLoading(false)
            }
        }
        loadMovie()
    }, [movieId, mounted])

    const handleRatingSubmit = async (rating: number) => {
        if (!user) {
            alert("Vui lòng đăng nhập để đánh giá")
            return
        }

        try {
            await addRating(user.id, movieId, rating)
            setRatingSubmitted(true)
        } catch (err) {
            console.error("Failed to submit rating:", err)
            alert("Không thể gửi đánh giá. Vui lòng thử lại.")
        }
    }

    if (!mounted || isLoading) {
        return (
            <div className="container mx-auto flex min-h-[400px] items-center justify-center px-4">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
        )
    }

    if (error || !movie) {
        return (
            <div className="container mx-auto px-4 py-8 text-center">
                <h1 className="text-2xl font-bold text-destructive">{error || "Phim không tồn tại"}</h1>
            </div>
        )
    }

    const gradient = generateGradient(movie.title)

    return (
        <div className="container mx-auto px-4 py-8">
            {/* Hero Section */}
            <div className="mb-12 grid gap-8 lg:grid-cols-[350px_1fr]">
                {/* Movie Poster (Gradient) */}
                <div
                    className="relative aspect-[2/3] w-full max-w-[350px] overflow-hidden rounded-2xl shadow-xl"
                    style={{ background: gradient }}
                >
                    <div className="absolute inset-0 flex flex-col items-center justify-center p-6 text-center text-white">
                        <h2 className="text-2xl font-bold leading-tight drop-shadow-lg">{movie.title}</h2>
                        {movie.year && <span className="mt-2 text-lg text-white/80">({movie.year})</span>}
                    </div>
                    <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent" />
                </div>

                {/* Movie Info */}
                <div className="flex flex-col">
                    <h1 className="text-3xl font-bold md:text-4xl">{movie.title}</h1>
                    {movie.year && <p className="mt-2 text-lg text-muted-foreground">Năm phát hành: {movie.year}</p>}

                    {/* Genres */}
                    <div className="mt-4 flex flex-wrap gap-2">
                        {movie.genres.map((genre) => (
                            <Badge key={genre} variant="secondary" className="text-sm">
                                {genre}
                            </Badge>
                        ))}
                    </div>

                    {/* Stats */}
                    <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
                        <div className="flex items-center gap-3 rounded-lg bg-muted/50 p-4">
                            <Star className="h-5 w-5 text-yellow-500" />
                            <div>
                                <p className="text-sm text-muted-foreground">Đánh giá</p>
                                <p className="text-xl font-bold">{movie.avgRating.toFixed(1)}/5</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-3 rounded-lg bg-muted/50 p-4">
                            <Users className="h-5 w-5 text-primary" />
                            <div>
                                <p className="text-sm text-muted-foreground">Lượt đánh giá</p>
                                <p className="text-xl font-bold">{movie.ratingCount.toLocaleString()}</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-3 rounded-lg bg-muted/50 p-4">
                            <Calendar className="h-5 w-5 text-green-500" />
                            <div>
                                <p className="text-sm text-muted-foreground">Năm</p>
                                <p className="text-xl font-bold">{movie.year || "N/A"}</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-3 rounded-lg bg-muted/50 p-4">
                            <TrendingUp className="h-5 w-5 text-orange-500" />
                            <div>
                                <p className="text-sm text-muted-foreground">Thể loại</p>
                                <p className="text-xl font-bold">{movie.genres.length}</p>
                            </div>
                        </div>
                    </div>

                    {/* Rating Input */}
                    <Card className="mt-8">
                        <CardHeader className="pb-3">
                            <CardTitle className="text-lg">Đánh giá phim này</CardTitle>
                        </CardHeader>
                        <CardContent>
                            {ratingSubmitted ? (
                                <div className="flex items-center gap-2 text-green-600">
                                    <CheckCircle className="h-5 w-5" />
                                    <span className="font-medium">Cảm ơn bạn đã đánh giá!</span>
                                </div>
                            ) : (
                                <RatingInput movieId={movieId} onSubmit={handleRatingSubmit} />
                            )}
                        </CardContent>
                    </Card>
                </div>
            </div>

            <Separator className="my-8" />

            {/* Similar Movies */}
            {similarMovies.length > 0 && (
                <section>
                    <h2 className="mb-6 text-2xl font-bold">Phim tương tự</h2>
                    <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
                        {similarMovies.map((m) => (
                            <MovieCard
                                key={m.movieId}
                                movie={{
                                    id: m.movieId,
                                    title: m.title,
                                    genres: m.genres,
                                    avgRating: m.avgRating,
                                    ratingCount: m.ratingCount || 0,
                                    year: m.year
                                }}
                                size="md"
                            />
                        ))}
                    </div>
                </section>
            )}
        </div>
    )
}
