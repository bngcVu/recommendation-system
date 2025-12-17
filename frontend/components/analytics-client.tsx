"use client"

import { useState, useEffect } from "react"
import { getStats, getRatingDistribution, getGenreFrequency, getTopMoviesAnalytics, type Analytics, type RatingDistribution, type GenreFrequency, type Movie } from "@/lib/api"
import { StatCard } from "@/components/stat-card"
import { RatingDistributionChart } from "@/components/charts/rating-distribution-chart"
import { TopGenresChart } from "@/components/charts/top-genres-chart"
import { TopMoviesChart } from "@/components/charts/top-movies-chart"
import { Film, Users, Star, BarChart3, Loader2 } from "lucide-react"

export function AnalyticsClient() {
  const [mounted, setMounted] = useState(false)
  const [stats, setStats] = useState<Analytics | null>(null)
  const [ratingDistribution, setRatingDistribution] = useState<RatingDistribution[]>([])
  const [genreFrequency, setGenreFrequency] = useState<GenreFrequency[]>([])
  const [topMovies, setTopMovies] = useState<Movie[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (!mounted) return

    async function loadAnalytics() {
      setIsLoading(true)
      try {
        const [statsData, ratingData, genreData, moviesData] = await Promise.all([
          getStats(),
          getRatingDistribution(),
          getGenreFrequency(),
          getTopMoviesAnalytics(10, 10)
        ])

        setStats(statsData)
        setRatingDistribution(ratingData.distribution)
        setGenreFrequency(genreData.genres.map(g => ({ genre: g.genre, count: g.count })))
        setTopMovies(moviesData.movies)
      } catch (err) {
        console.error("Failed to load analytics:", err)
      } finally {
        setIsLoading(false)
      }
    }
    loadAnalytics()
  }, [mounted])

  if (!mounted || isLoading) {
    return (
      <div className="flex min-h-[400px] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Stats Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Tổng số phim"
          value={stats?.totalMovies?.toLocaleString() || "0"}
          icon={Film}
          description="Trong hệ thống"
        />
        <StatCard
          title="Tổng người dùng"
          value={stats?.totalUsers?.toLocaleString() || "0"}
          icon={Users}
          description="Đã đăng ký"
        />
        <StatCard
          title="Tổng đánh giá"
          value={stats?.totalRatings?.toLocaleString() || "0"}
          icon={BarChart3}
          description="Từ người dùng"
        />
        <StatCard
          title="Rating trung bình"
          value={stats?.avgRating?.toFixed(2) || "0.00"}
          icon={Star}
          description="Trên 5 sao"
        />
      </div>

      {/* Charts Grid */}
      <div className="grid gap-6 lg:grid-cols-2">
        <RatingDistributionChart data={ratingDistribution} />
        <TopGenresChart data={genreFrequency} />
      </div>

      {/* Full Width Chart */}
      <TopMoviesChart movies={topMovies.map(m => ({
        id: m.movieId,
        title: m.title,
        genres: m.genres,
        avgRating: m.avgRating,
        ratingCount: m.ratingCount
      }))} />
    </div>
  )
}
