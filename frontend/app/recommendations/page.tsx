import type { Metadata } from "next"
import { RecommendationsClient } from "@/components/recommendations-client"

export const metadata: Metadata = {
  title: "Gợi ý phim - MovieRec",
  description: "Nhận gợi ý phim từ 4 mô hình khác nhau",
}

export default function RecommendationsPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Gợi ý phim</h1>
        <p className="mt-2 text-muted-foreground">
          Chọn người dùng và xem gợi ý phim từ các mô hình recommendation khác nhau
        </p>
      </div>
      <RecommendationsClient />
    </div>
  )
}
