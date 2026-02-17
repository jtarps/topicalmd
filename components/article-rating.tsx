"use client"

import { useState } from "react"
import { ThumbsUp, ThumbsDown } from "lucide-react"

interface ArticleRatingProps {
  documentId: string
  initialYes?: number
  initialNo?: number
}

export default function ArticleRating({ documentId, initialYes = 0, initialNo = 0 }: ArticleRatingProps) {
  const [voted, setVoted] = useState<"yes" | "no" | null>(null)
  const [yesCount, setYesCount] = useState(initialYes)
  const [noCount, setNoCount] = useState(initialNo)
  const [submitting, setSubmitting] = useState(false)

  const handleVote = async (vote: "yes" | "no") => {
    if (voted || submitting) return
    setSubmitting(true)

    try {
      const res = await fetch("/api/rate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ documentId, vote }),
      })

      if (res.ok) {
        setVoted(vote)
        if (vote === "yes") setYesCount((c) => c + 1)
        else setNoCount((c) => c + 1)
      }
    } catch {
      // Silently fail — non-critical feature
    } finally {
      setSubmitting(false)
    }
  }

  const total = yesCount + noCount

  return (
    <div className="medical-card p-5 text-center">
      <p className="font-medium mb-3">Was this article helpful?</p>

      {voted ? (
        <div>
          <p className="text-sm text-gray-600 mb-3">Thanks for your feedback!</p>
          {total > 0 && (
            <div className="flex items-center justify-center gap-4 text-sm text-gray-500">
              <span className="flex items-center gap-1">
                <ThumbsUp className="h-4 w-4 text-green-600" />
                {yesCount}
              </span>
              <span className="flex items-center gap-1">
                <ThumbsDown className="h-4 w-4 text-red-500" />
                {noCount}
              </span>
              <span className="text-gray-400">
                {total > 0 ? Math.round((yesCount / total) * 100) : 0}% found helpful
              </span>
            </div>
          )}
        </div>
      ) : (
        <div className="flex items-center justify-center gap-3">
          <button
            onClick={() => handleVote("yes")}
            disabled={submitting}
            className="flex items-center gap-2 px-4 py-2 rounded-lg border border-green-200 bg-green-50 hover:bg-green-100 text-green-700 font-medium transition-colors disabled:opacity-50"
          >
            <ThumbsUp className="h-4 w-4" />
            Yes
          </button>
          <button
            onClick={() => handleVote("no")}
            disabled={submitting}
            className="flex items-center gap-2 px-4 py-2 rounded-lg border border-red-200 bg-red-50 hover:bg-red-100 text-red-700 font-medium transition-colors disabled:opacity-50"
          >
            <ThumbsDown className="h-4 w-4" />
            No
          </button>
        </div>
      )}
    </div>
  )
}
