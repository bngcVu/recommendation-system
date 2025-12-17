"use client"

import { useState, useEffect, useRef } from "react"
import { getTopMovies, type Movie } from "@/lib/api"
import { MovieCard } from "@/components/movie-card"
import { ChevronLeft, ChevronRight, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"

export function TopRatedMovies() {
  const scrollContainerRef = useRef<HTMLDivElement>(null)
  const [topRated, setTopRated] = useState<Movie[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    async function loadTopMovies() {
      setIsLoading(true)
      try {
        const data = await getTopMovies(15)
        setTopRated(data.movies)
      } catch (err) {
        console.error("Failed to load top movies:", err)
      } finally {
        setIsLoading(false)
      }
    }
    loadTopMovies()
  }, [])

  const scroll = (direction: "left" | "right") => {
    if (scrollContainerRef.current) {
      const scrollAmount = 300
      scrollContainerRef.current.scrollBy({
        left: direction === "left" ? -scrollAmount : scrollAmount,
        behavior: "smooth",
      })
    }
  }

  return (
    <section className="py-12 md:py-16">
      <div className="container mx-auto px-4">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold md:text-3xl">Phim được đánh giá cao</h2>
            <p className="mt-1 text-muted-foreground">Những bộ phim nhận được đánh giá tốt nhất từ người dùng</p>
          </div>
          <div className="hidden gap-2 md:flex">
            <Button variant="outline" size="icon" onClick={() => scroll("left")}>
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="icon" onClick={() => scroll("right")}>
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="flex min-h-[200px] items-center justify-center">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        )}

        {/* Scrollable Container */}
        {!isLoading && (
          <div
            ref={scrollContainerRef}
            className="flex gap-4 overflow-x-auto pb-4 scrollbar-hide"
            style={{ scrollbarWidth: "none", msOverflowStyle: "none" }}
          >
            {topRated.map((movie) => (
              <div key={movie.movieId} className="flex-shrink-0">
                <MovieCard
                  movie={{
                    id: movie.movieId,
                    title: movie.title,
                    genres: movie.genres,
                    avgRating: movie.avgRating,
                    ratingCount: movie.ratingCount,
                    year: movie.year
                  }}
                  size="md"
                />
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  )
}
