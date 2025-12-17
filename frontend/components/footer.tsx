import { Film } from "lucide-react"
import Link from "next/link"

export function Footer() {
  return (
    <footer className="border-t border-border bg-muted/30">
      <div className="container mx-auto px-4 py-8">
        <div className="flex flex-col items-center justify-between gap-4 md:flex-row">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
              <Film className="h-4 w-4 text-primary-foreground" />
            </div>
            <span className="font-semibold">MovieRec</span>
          </div>
          <nav className="flex gap-6 text-sm text-muted-foreground">
            <Link href="/" className="hover:text-foreground transition-colors">
              Trang chủ
            </Link>
            <Link href="/recommendations" className="hover:text-foreground transition-colors">
              Gợi ý
            </Link>
            <Link href="/analytics" className="hover:text-foreground transition-colors">
              Phân tích
            </Link>
          </nav>
          <div className="text-sm text-muted-foreground"></div>
        </div>
      </div>
    </footer>
  )
}
