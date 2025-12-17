import { HeroSection } from "@/components/hero-section"
import { TopRatedMovies } from "@/components/top-rated-movies"
import { RecommendedMovies } from "@/components/recommended-movies"

export default function HomePage() {
  return (
    <div className="flex flex-col">
      <HeroSection />
      <TopRatedMovies />
      <RecommendedMovies />
    </div>
  )
}
