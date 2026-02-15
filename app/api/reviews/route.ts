import { type NextRequest, NextResponse } from "next/server"
import { createClient } from "next-sanity"

export const dynamic = "force-dynamic"

const client = createClient({
  projectId: process.env.NEXT_PUBLIC_SANITY_PROJECT_ID || process.env.SANITY_PROJECT_ID,
  dataset: process.env.NEXT_PUBLIC_SANITY_DATASET || process.env.SANITY_DATASET || "production",
  apiVersion: "2023-05-03",
  useCdn: process.env.NODE_ENV === "production",
})

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams
  const brand = searchParams.get("brand")
  const minRating = searchParams.get("minRating") ? Number.parseInt(searchParams.get("minRating") || "0") : 0
  const sort = searchParams.get("sort") || "newest"

  try {
    // Build filter conditions
    const filterConditions = []

    if (brand) {
      filterConditions.push(`product->brand == "${brand}"`)
    }

    if (minRating > 0) {
      filterConditions.push(`rating >= ${minRating}`)
    }

    const filterString = filterConditions.length > 0 ? `&& ${filterConditions.join(" && ")}` : ""

    // Determine sort order
    let sortOrder = ""
    switch (sort) {
      case "newest":
        sortOrder = "publishedAt desc"
        break
      case "oldest":
        sortOrder = "publishedAt asc"
        break
      case "rating-high":
        sortOrder = "rating desc"
        break
      case "rating-low":
        sortOrder = "rating asc"
        break
      default:
        sortOrder = "publishedAt desc"
    }

    // Build and execute query
    const query = `{
      "reviews": *[_type == "review" ${filterString}] | order(${sortOrder}) {
        _id,
        title,
        "slug": slug.current,
        excerpt,
        mainImage,
        rating,
        product->{
          brand
        }
      }
    }`

    const data = await client.fetch(query)
    return NextResponse.json(data)
  } catch (error) {
    console.error("Error fetching reviews:", error)
    return NextResponse.json({ error: "Failed to fetch reviews", reviews: [] }, { status: 500 })
  }
}
