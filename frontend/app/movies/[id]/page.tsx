import type { Metadata } from "next"
import { MovieDetailWrapper } from "@/components/movie-detail-wrapper"

interface MoviePageProps {
  params: Promise<{ id: string }>
}

export async function generateMetadata({ params }: MoviePageProps): Promise<Metadata> {
  const { id } = await params

  // Try to fetch movie from API for metadata
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api'}/movies/${id}`, {
      cache: 'no-store'
    })
    if (res.ok) {
      const movie = await res.json()
      return {
        title: `${movie.title} - MovieRec`,
        description: `Xem thông tin chi tiết và đánh giá phim ${movie.title}`,
      }
    }
  } catch {
    // Fallback
  }

  return { title: "Chi tiết phim - MovieRec" }
}

export default async function MoviePage({ params }: MoviePageProps) {
  const { id } = await params
  return <MovieDetailWrapper movieId={parseInt(id)} />
}
