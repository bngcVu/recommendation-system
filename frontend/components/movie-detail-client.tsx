"use client"

import { useState } from "react"
import type { Movie } from "@/lib/mock-data"
import { MovieCard } from "@/components/movie-card"
import { RatingInput } from "@/components/rating-input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Star, Users, Calendar, TrendingUp, CheckCircle } from "lucide-react"

interface MovieDetailClientProps {
  movie: Movie
  similarMovies: Movie[]
  gradient: string
}

export function MovieDetailClient({ movie, similarMovies, gradient }: MovieDetailClientProps) {
  const [ratingSubmitted, setRatingSubmitted] = useState(false)

  const handleRatingSubmit = (rating: number) => {
    console.log(`Submitted rating ${rating} for movie ${movie.id}`)
    setRatingSubmitted(true)
  }

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
                <RatingInput movieId={movie.id} onSubmit={handleRatingSubmit} />
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
            {similarMovies.map((movie) => (
              <MovieCard key={movie.id} movie={movie} size="md" />
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
