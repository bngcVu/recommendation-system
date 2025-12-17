"use client"

import { useState, useEffect } from "react"
import { SearchBar } from "@/components/search-bar"
import { getStats, type Analytics } from "@/lib/api"

export function HeroSection() {
  const [stats, setStats] = useState<Analytics | null>(null)

  useEffect(() => {
    async function loadStats() {
      try {
        const data = await getStats()
        setStats(data)
      } catch (err) {
        console.error("Failed to load stats:", err)
      }
    }
    loadStats()
  }, [])

  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-primary/10 via-background to-background">
      {/* Background decorative elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -left-20 -top-20 h-64 w-64 rounded-full bg-primary/5 blur-3xl" />
        <div className="absolute -bottom-20 -right-20 h-64 w-64 rounded-full bg-primary/5 blur-3xl" />
      </div>

      <div className="container relative mx-auto px-4 py-20 md:py-32">
        <div className="mx-auto max-w-3xl text-center">
          <h1 className="text-balance text-4xl font-bold tracking-tight md:text-5xl lg:text-6xl">
            Khám phá phim
            <span className="text-primary"> yêu thích</span>
          </h1>
          <p className="mt-6 text-pretty text-lg text-muted-foreground md:text-xl">
            Hệ thống gợi ý phim thông minh giúp bạn tìm kiếm những bộ phim phù hợp với sở thích cá nhân.
          </p>

          {/* Search Bar */}
          <div className="mx-auto mt-10 max-w-xl">
            <SearchBar placeholder="Tìm kiếm phim theo tên..." className="shadow-lg" />
          </div>

          {/* Quick Stats */}
          <div className="mt-12 flex flex-wrap items-center justify-center gap-8 text-sm text-muted-foreground">
            <div className="flex items-center gap-2">
              <span className="text-2xl font-bold text-foreground">
                {stats ? stats.totalMovies.toLocaleString() : "---"}
              </span>
              <span>Phim</span>
            </div>
            <div className="h-4 w-px bg-border" />
            <div className="flex items-center gap-2">
              <span className="text-2xl font-bold text-foreground">
                {stats ? stats.totalUsers.toLocaleString() : "---"}
              </span>
              <span>Người dùng</span>
            </div>
            <div className="h-4 w-px bg-border" />
            <div className="flex items-center gap-2">
              <span className="text-2xl font-bold text-foreground">4</span>
              <span>Mô hình gợi ý</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
