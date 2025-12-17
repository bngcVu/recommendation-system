import type { Metadata } from "next"
import { AnalyticsClient } from "@/components/analytics-client"

export const metadata: Metadata = {
  title: "Phân tích dữ liệu - MovieRec",
  description: "Xem trực quan hóa và phân tích dữ liệu hệ thống gợi ý phim",
}

export default function AnalyticsPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Phân tích dữ liệu</h1>
        <p className="mt-2 text-muted-foreground">Trực quan hóa thống kê và phân tích dữ liệu từ hệ thống gợi ý phim</p>
      </div>
      <AnalyticsClient />
    </div>
  )
}
