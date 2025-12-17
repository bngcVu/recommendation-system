"use client"

import { useState, useEffect } from "react"
import { getRecommendations, type Recommendation } from "@/lib/api"
import { MovieCard } from "@/components/movie-card"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { ArrowRight, Loader2 } from "lucide-react"

export function RecommendedMovies() {
  const [recommended, setRecommended] = useState<Recommendation[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    async function loadRecommendations() {
      setIsLoading(true)
      try {
        // Default to user 1 for home page preview, or use top movies
        const data = await getRecommendations(1, { model: 'hybrid', n: 8 })
        setRecommended(data.recommendations)
      } catch (err) {
        console.error("Failed to load recommendations:", err)
      } finally {
        setIsLoading(false)
      }
    }
    loadRecommendations()
  }, [])

  return (
    <section className="bg-muted/30 py-12 md:py-16">
      <div className="container mx-auto px-4">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold md:text-3xl">Gợi ý cho bạn</h2>
            <p className="mt-1 text-muted-foreground">Những bộ phim có thể bạn sẽ thích</p>
          </div>
          <Link href="/recommendations">
            <Button variant="outline" className="gap-2 bg-transparent">
              Xem tất cả
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="flex min-h-[200px] items-center justify-center">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        )}

        {/* Grid of movie cards */}
        {!isLoading && (
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
            {recommended.map((movie) => (
              <MovieCard
                key={movie.movieId}
                movie={{
                  id: movie.movieId,
                  title: movie.title,
                  genres: movie.genres,
                  avgRating: movie.avgRating,
                  ratingCount: movie.ratingCount || 0,
                  year: movie.year
                }}
                size="md"
              />
            ))}
          </div>
        )}
      </div>
    </section>
  )
}
