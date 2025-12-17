"use client"

import { useState, useEffect } from "react"
import { type Recommendation, type RatingHistoryItem, getRecommendations, getUserHistory, getGenres } from "@/lib/api"
import { MovieCard } from "@/components/movie-card"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Star, History, Filter, User, Loader2 } from "lucide-react"
import { useAuth } from "@/contexts/auth-context"
import { LoginDialog } from "@/components/login-dialog"
import { Button } from "@/components/ui/button"

const recommendationModels = [
  {
    id: "content_based",
    name: "Content-Based",
    description: "Gợi ý dựa trên nội dung phim (genres, keywords)",
  },
  {
    id: "item_based",
    name: "Item-Based CF",
    description: "Gợi ý dựa trên sự tương đồng giữa các phim",
  },
  {
    id: "user_based",
    name: "User-Based CF",
    description: "Gợi ý dựa trên sở thích của người dùng tương tự",
  },
  {
    id: "hybrid",
    name: "Hybrid",
    description: "Kết hợp nhiều phương pháp để tối ưu kết quả",
  },
]

export function RecommendationsClient() {
  const { user, isLoading: authLoading } = useAuth()
  const [mounted, setMounted] = useState(false)
  const [selectedModel, setSelectedModel] = useState("hybrid")
  const [selectedGenre, setSelectedGenre] = useState<string | null>(null)
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [userHistory, setUserHistory] = useState<RatingHistoryItem[]>([])
  const [genres, setGenres] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const userId = user?.id || null

  useEffect(() => {
    setMounted(true)
  }, [])

  // Load genres on mount
  useEffect(() => {
    if (!mounted) return

    async function loadGenres() {
      try {
        const data = await getGenres()
        setGenres(data.genres)
      } catch (err) {
        console.error("Failed to load genres:", err)
      }
    }
    loadGenres()
  }, [mounted])

  // Load recommendations when user or model changes
  useEffect(() => {
    if (!mounted || !userId) {
      setIsLoading(false)
      return
    }

    async function loadRecommendations() {
      setIsLoading(true)
      setError(null)
      try {
        const data = await getRecommendations(userId, { model: selectedModel, n: 12 })
        let recs = data.recommendations

        // Filter by genre if selected
        if (selectedGenre) {
          recs = recs.filter(m => m.genres.includes(selectedGenre))
        }

        setRecommendations(recs)
      } catch (err) {
        console.error("Failed to load recommendations:", err)
        setError("Không thể tải gợi ý. Vui lòng thử lại sau.")
        setRecommendations([])
      } finally {
        setIsLoading(false)
      }
    }
    loadRecommendations()
  }, [userId, selectedModel, selectedGenre, mounted])

  // Load user history
  useEffect(() => {
    if (!userId) return

    async function loadHistory() {
      try {
        const data = await getUserHistory(userId, 10)
        setUserHistory(data.history)
      } catch (err) {
        console.error("Failed to load history:", err)
      }
    }
    loadHistory()
  }, [userId])

  if (!mounted || authLoading) {
    return (
      <div className="flex min-h-[400px] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (!user) {
    return (
      <Card className="mx-auto max-w-md">
        <CardContent className="py-12 text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
            <User className="h-8 w-8 text-primary" />
          </div>
          <h3 className="mb-2 text-xl font-semibold">Đăng nhập để xem gợi ý</h3>
          <p className="mb-6 text-muted-foreground">
            Vui lòng đăng nhập để nhận gợi ý phim được cá nhân hóa dựa trên sở thích của bạn
          </p>
          <LoginDialog
            trigger={
              <Button size="lg" className="gap-2">
                <User className="h-4 w-4" />
                Đăng nhập ngay
              </Button>
            }
          />
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="grid gap-8 lg:grid-cols-[300px_1fr]">
      {/* Sidebar - User Info & Filters */}
      <div className="space-y-6">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">Xin chào!</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-3 rounded-lg bg-primary/10 p-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary">
                <User className="h-5 w-5 text-primary-foreground" />
              </div>
              <div>
                <p className="font-medium">{user.name}</p>
                <p className="text-sm text-muted-foreground">User ID: {user.id}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Genre Filter */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-lg">
              <Filter className="h-4 w-4" />
              Lọc theo thể loại
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Select value={selectedGenre || "all"} onValueChange={(v) => setSelectedGenre(v === "all" ? null : v)}>
              <SelectTrigger>
                <SelectValue placeholder="Tất cả thể loại" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tất cả thể loại</SelectItem>
                {genres.map((genre) => (
                  <SelectItem key={genre} value={genre}>
                    {genre}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </CardContent>
        </Card>

        {/* User Rating History */}
        {userHistory.length > 0 && (
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-lg">
                <History className="h-4 w-4" />
                Lịch sử đánh giá
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {userHistory.slice(0, 5).map((item) => (
                <div key={item.movieId} className="flex items-center justify-between rounded-lg bg-muted/50 p-3">
                  <div className="min-w-0 flex-1">
                    <p className="truncate font-medium text-sm">{item.title}</p>
                    <p className="text-xs text-muted-foreground">
                      {new Date(item.timestamp).toLocaleDateString('vi-VN')}
                    </p>
                  </div>
                  <div className="flex items-center gap-1">
                    <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                    <span className="text-sm font-medium">{item.userRating}</span>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        )}
      </div>

      {/* Main Content - Recommendations */}
      <div>
        <Tabs value={selectedModel} onValueChange={setSelectedModel}>
          <TabsList className="mb-6 grid w-full grid-cols-2 lg:grid-cols-4">
            {recommendationModels.map((model) => (
              <TabsTrigger key={model.id} value={model.id} className="text-sm">
                {model.name}
              </TabsTrigger>
            ))}
          </TabsList>

          {recommendationModels.map((model) => (
            <TabsContent key={model.id} value={model.id}>
              {/* Model Description */}
              <Card className="mb-6">
                <CardContent className="py-4">
                  <div className="flex items-center gap-3">
                    <Badge variant="secondary">{model.name}</Badge>
                    <span className="text-sm text-muted-foreground">{model.description}</span>
                  </div>
                </CardContent>
              </Card>

              {/* Loading State */}
              {isLoading && (
                <div className="flex min-h-[200px] items-center justify-center">
                  <Loader2 className="h-8 w-8 animate-spin text-primary" />
                </div>
              )}

              {/* Error State */}
              {error && !isLoading && (
                <Card className="flex min-h-[200px] items-center justify-center">
                  <CardContent className="text-center">
                    <p className="text-destructive">{error}</p>
                  </CardContent>
                </Card>
              )}

              {/* Recommendation Results */}
              {!isLoading && !error && recommendations.length > 0 && (
                <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4">
                  {recommendations.map((movie) => (
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

              {/* Empty State */}
              {!isLoading && !error && recommendations.length === 0 && (
                <Card className="flex min-h-[200px] items-center justify-center">
                  <CardContent className="text-center">
                    <p className="text-muted-foreground">Không tìm thấy gợi ý phù hợp</p>
                  </CardContent>
                </Card>
              )}
            </TabsContent>
          ))}
        </Tabs>
      </div>
    </div>
  )
}
