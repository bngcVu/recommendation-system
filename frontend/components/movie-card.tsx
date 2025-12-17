"use client"

import Link from "next/link"
import { Star } from "lucide-react"
import { type Movie, generateGradient } from "@/lib/mock-data"
import { Badge } from "@/components/ui/badge"

interface MovieCardProps {
  movie: Movie
  size?: "sm" | "md" | "lg"
}

export function MovieCard({ movie, size = "md" }: MovieCardProps) {
  const sizeClasses = {
    sm: "h-48 w-36",
    md: "h-64 w-44",
    lg: "h-80 w-56",
  }

  return (
    <Link href={`/movies/${movie.id}`} className="group">
      <div
        className={`relative overflow-hidden rounded-xl ${sizeClasses[size]} transition-all duration-300 group-hover:scale-105 group-hover:shadow-lg`}
        style={{ background: generateGradient(movie.title) }}
      >
        {/* Movie Title Overlay */}
        <div className="absolute inset-0 flex flex-col items-center justify-center p-4 text-center text-white">
          <h3 className="text-sm font-bold leading-tight drop-shadow-lg md:text-base">{movie.title}</h3>
          {movie.year && <span className="mt-1 text-xs text-white/80">({movie.year})</span>}
        </div>

        {/* Rating Badge */}
        <div className="absolute right-2 top-2 flex items-center gap-1 rounded-full bg-black/50 px-2 py-1 backdrop-blur-sm">
          <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
          <span className="text-xs font-semibold text-white">{movie.avgRating.toFixed(1)}</span>
        </div>

        {/* Gradient Overlay for better text readability */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent" />
      </div>

      {/* Genres */}
      <div className="mt-2 flex flex-wrap gap-1">
        {movie.genres.slice(0, 2).map((genre) => (
          <Badge key={genre} variant="secondary" className="text-xs">
            {genre}
          </Badge>
        ))}
      </div>
    </Link>
  )
}
