"use client"

import { useState, useEffect, useRef, useCallback } from "react"
import { Search, X, Loader2 } from "lucide-react"
import { Input } from "@/components/ui/input"
import { searchMovies, type Movie } from "@/lib/api"
import Link from "next/link"
import { Star } from "lucide-react"

interface SearchBarProps {
  placeholder?: string
  className?: string
}

// Custom debounce hook
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay)
    return () => clearTimeout(timer)
  }, [value, delay])

  return debouncedValue
}

export function SearchBar({ placeholder = "Tìm kiếm phim...", className }: SearchBarProps) {
  const [query, setQuery] = useState("")
  const [suggestions, setSuggestions] = useState<Movie[]>([])
  const [isOpen, setIsOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const wrapperRef = useRef<HTMLDivElement>(null)

  const debouncedQuery = useDebounce(query, 300)

  // Search when debounced query changes
  useEffect(() => {
    if (debouncedQuery.length > 1) {
      setIsLoading(true)
      searchMovies(debouncedQuery, 5)
        .then((data) => {
          setSuggestions(data.movies)
          setIsOpen(true)
        })
        .catch((err) => {
          console.error("Search error:", err)
          setSuggestions([])
        })
        .finally(() => setIsLoading(false))
    } else {
      setSuggestions([])
      setIsOpen(false)
    }
  }, [debouncedQuery])

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  return (
    <div ref={wrapperRef} className={`relative ${className}`}>
      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          type="text"
          placeholder={placeholder}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => query.length > 1 && suggestions.length > 0 && setIsOpen(true)}
          className="pl-10 pr-10"
        />
        {isLoading && (
          <Loader2 className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 animate-spin text-muted-foreground" />
        )}
        {!isLoading && query && (
          <button
            onClick={() => {
              setQuery("")
              setSuggestions([])
              setIsOpen(false)
            }}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* Suggestions Dropdown */}
      {isOpen && suggestions.length > 0 && (
        <div className="absolute top-full z-50 mt-2 w-full overflow-hidden rounded-lg border border-border bg-popover shadow-lg">
          {suggestions.map((movie) => (
            <Link
              key={movie.movieId}
              href={`/movies/${movie.movieId}`}
              onClick={() => {
                setQuery("")
                setIsOpen(false)
              }}
              className="flex items-center justify-between px-4 py-3 hover:bg-accent transition-colors"
            >
              <div>
                <p className="font-medium">{movie.title}</p>
                <p className="text-sm text-muted-foreground">{movie.genres.join(", ")}</p>
              </div>
              <div className="flex items-center gap-1">
                <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                <span className="text-sm font-medium">{movie.avgRating.toFixed(1)}</span>
              </div>
            </Link>
          ))}
        </div>
      )}

      {/* No results */}
      {isOpen && !isLoading && query.length > 1 && suggestions.length === 0 && (
        <div className="absolute top-full z-50 mt-2 w-full overflow-hidden rounded-lg border border-border bg-popover p-4 shadow-lg text-center text-muted-foreground">
          Không tìm thấy phim phù hợp
        </div>
      )}
    </div>
  )
}
