"use client"

import { useState } from "react"
import { Star } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

interface RatingInputProps {
  movieId: number
  currentRating?: number
  onSubmit?: (rating: number) => void
}

export function RatingInput({ movieId, currentRating = 0, onSubmit }: RatingInputProps) {
  const [rating, setRating] = useState(currentRating)
  const [hoverRating, setHoverRating] = useState(0)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async () => {
    if (rating === 0) return
    setIsSubmitting(true)
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 500))
    onSubmit?.(rating)
    setIsSubmitting(false)
  }

  const displayRating = hoverRating || rating

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            type="button"
            className="p-1 transition-transform hover:scale-110"
            onMouseEnter={() => setHoverRating(star)}
            onMouseLeave={() => setHoverRating(0)}
            onClick={() => setRating(star)}
          >
            <Star
              className={cn(
                "h-6 w-6 transition-colors",
                star <= displayRating ? "fill-yellow-400 text-yellow-400" : "text-muted-foreground",
              )}
            />
          </button>
        ))}
        {displayRating > 0 && <span className="ml-2 text-sm font-medium text-muted-foreground">{displayRating}/5</span>}
      </div>
      <Button onClick={handleSubmit} disabled={rating === 0 || isSubmitting} size="sm" className="w-fit">
        {isSubmitting ? "Đang gửi..." : "Gửi đánh giá"}
      </Button>
    </div>
  )
}
