"use client"

import { useState, useEffect } from "react"
import { useSearchParams } from "next/navigation"
import Image from "next/image"
import Link from "next/link"
import { urlForImage } from "@/lib/sanity-image"
import { Loader2 } from "lucide-react"

type SearchResult = {
  _id: string
  _type: string
  title: string
  slug: string
  excerpt?: string
  mainImage?: any
}

type SearchResponse = {
  total: number
  results: SearchResult[]
}

export default function SearchPage() {
  const searchParams = useSearchParams()
  const query = searchParams.get("q") || ""
  const [type, setType] = useState<string>("all")
  const [results, setResults] = useState<SearchResult[]>([])
  const [total, setTotal] = useState<number>(0)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState<number>(1)
  const pageSize = 10

  useEffect(() => {
    if (!query) return

    const fetchResults = async () => {
      setLoading(true)
      setError(null)

      try {
        const response = await fetch(
          `/api/search?q=${encodeURIComponent(query)}&type=${type}&page=${page}&pageSize=${pageSize}`,
        )

        if (!response.ok) {
          throw new Error("Failed to fetch search results")
        }

        const data: SearchResponse = await response.json()
        setResults(data.results || [])
        setTotal(data.total || 0)
      } catch (err) {
        setError("An error occurred while searching. Please try again.")
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    fetchResults()
  }, [query, type, page])

  const handleTypeChange = (newType: string) => {
    setType(newType)
    setPage(1)
  }

  const totalPages = Math.ceil(total / pageSize)

  const getUrlForContentType = (type: string, slug: string): string => {
    switch (type) {
      case "review":
        return `/review/${slug}`
      case "useCase":
        return `/best-for/${slug}`
      case "comparison":
        return `/compare/${slug}`
      case "ingredient":
        return `/ingredient/${slug}`
      case "faq":
        return `/faq/${slug}`
      default:
        return "/"
    }
  }

  const getContentTypeLabel = (type: string): string => {
    switch (type) {
      case "review":
        return "Review"
      case "useCase":
        return "Best For"
      case "comparison":
        return "Comparison"
      case "ingredient":
        return "Ingredient"
      case "faq":
        return "FAQ"
      default:
        return type
    }
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6 text-primary">{query ? `Search results for "${query}"` : "Search"}</h1>

        <div className="mb-8">
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => handleTypeChange("all")}
              className={`px-4 py-2 rounded-full text-sm ${
                type === "all" ? "bg-primary text-white" : "bg-gray-100 text-gray-800 hover:bg-gray-200"
              }`}
            >
              All
            </button>
            <button
              onClick={() => handleTypeChange("review")}
              className={`px-4 py-2 rounded-full text-sm ${
                type === "review" ? "bg-primary text-white" : "bg-gray-100 text-gray-800 hover:bg-gray-200"
              }`}
            >
              Reviews
            </button>
            <button
              onClick={() => handleTypeChange("useCase")}
              className={`px-4 py-2 rounded-full text-sm ${
                type === "useCase" ? "bg-primary text-white" : "bg-gray-100 text-gray-800 hover:bg-gray-200"
              }`}
            >
              Best For
            </button>
            <button
              onClick={() => handleTypeChange("comparison")}
              className={`px-4 py-2 rounded-full text-sm ${
                type === "comparison" ? "bg-primary text-white" : "bg-gray-100 text-gray-800 hover:bg-gray-200"
              }`}
            >
              Comparisons
            </button>
            <button
              onClick={() => handleTypeChange("ingredient")}
              className={`px-4 py-2 rounded-full text-sm ${
                type === "ingredient" ? "bg-primary text-white" : "bg-gray-100 text-gray-800 hover:bg-gray-200"
              }`}
            >
              Ingredients
            </button>
            <button
              onClick={() => handleTypeChange("faq")}
              className={`px-4 py-2 rounded-full text-sm ${
                type === "faq" ? "bg-primary text-white" : "bg-gray-100 text-gray-800 hover:bg-gray-200"
              }`}
            >
              FAQs
            </button>
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center items-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : error ? (
          <div className="medical-danger p-4 rounded-md">{error}</div>
        ) : results.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-xl text-gray-600">No results found for "{query}"</p>
            <p className="mt-2 text-gray-500">Try different keywords or filters</p>
          </div>
        ) : (
          <>
            <p className="mb-4 text-gray-600">
              Found {total} result{total !== 1 ? "s" : ""}
            </p>
            <div className="space-y-6">
              {results.map((result) => (
                <Link
                  key={result._id}
                  href={getUrlForContentType(result._type, result.slug)}
                  className="medical-card block p-6 hover:bg-blue-50 transition-colors"
                >
                  <div className="flex gap-4">
                    {result.mainImage && (
                      <div className="relative h-24 w-24 flex-shrink-0">
                        <Image
                          src={urlForImage(result.mainImage).width(200).height(200).url() || "/placeholder.svg"}
                          alt={result.title}
                          fill
                          className="object-cover rounded-md"
                          sizes="96px"
                        />
                      </div>
                    )}
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="medical-tag">{getContentTypeLabel(result._type)}</span>
                      </div>
                      <h2 className="text-xl font-medium hover:text-primary transition-colors">{result.title}</h2>
                      {result.excerpt && <p className="mt-2 text-gray-600 line-clamp-2">{result.excerpt}</p>}
                    </div>
                  </div>
                </Link>
              ))}
            </div>

            {totalPages > 1 && (
              <div className="flex justify-center mt-8">
                <nav className="inline-flex rounded-md shadow">
                  <button
                    onClick={() => setPage(Math.max(1, page - 1))}
                    disabled={page === 1}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-l-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  <div className="flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border-t border-b border-gray-300">
                    Page {page} of {totalPages}
                  </div>
                  <button
                    onClick={() => setPage(Math.min(totalPages, page + 1))}
                    disabled={page === totalPages}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-r-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next
                  </button>
                </nav>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
