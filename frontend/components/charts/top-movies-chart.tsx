"use client"

import { Bar, BarChart, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import type { Movie } from "@/lib/mock-data"

const GRADIENT_ID = "topMoviesGradient"

interface TopMoviesChartProps {
  movies: Movie[]
}

export function TopMoviesChart({ movies }: TopMoviesChartProps) {
  const chartData = movies
    .sort((a, b) => b.avgRating - a.avgRating)
    .map((movie) => ({
      name: movie.title.length > 20 ? movie.title.slice(0, 20) + "..." : movie.title,
      fullName: movie.title,
      rating: movie.avgRating,
      ratingCount: movie.ratingCount,
    }))

  return (
    <Card>
      <CardHeader>
        <CardTitle>Top phim được đánh giá cao</CardTitle>
        <CardDescription>Các phim có điểm đánh giá trung bình cao nhất</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-[400px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} layout="vertical" margin={{ top: 10, right: 30, left: 120, bottom: 0 }}>
              <defs>
                <linearGradient id={GRADIENT_ID} x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor="#06b6d4" stopOpacity={0.8} />
                  <stop offset="100%" stopColor="#3b82f6" stopOpacity={0.9} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="hsl(var(--border))" />
              <XAxis
                type="number"
                domain={[0, 5]}
                tickLine={false}
                axisLine={false}
                fontSize={12}
                tick={{ fill: "hsl(var(--muted-foreground))" }}
              />
              <YAxis
                type="category"
                dataKey="name"
                tickLine={false}
                axisLine={false}
                fontSize={11}
                tick={{ fill: "hsl(var(--muted-foreground))" }}
                width={110}
              />
              <Tooltip
                cursor={{ fill: "hsl(var(--muted))", opacity: 0.3 }}
                contentStyle={{
                  backgroundColor: "hsl(var(--popover))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "8px",
                }}
                labelStyle={{ color: "hsl(var(--foreground))" }}
                formatter={(value: number, name: string) => {
                  if (name === "rating") return [value.toFixed(2), "Rating"]
                  return [value, name]
                }}
                labelFormatter={(_, payload) => {
                  if (payload && payload[0]) {
                    return payload[0].payload.fullName
                  }
                  return ""
                }}
              />
              <Bar dataKey="rating" fill={`url(#${GRADIENT_ID})`} radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}
