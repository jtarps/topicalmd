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
  const category = searchParams.get("category")
  const sort = searchParams.get("sort") || "newest"

  try {
    // Build filter conditions
    const filterConditions = []

    if (category) {
      filterConditions.push(`"${category}" in categories`)
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
      case "a-z":
        sortOrder = "title asc"
        break
      case "z-a":
        sortOrder = "title desc"
        break
      default:
        sortOrder = "publishedAt desc"
    }

    // Build and execute query
    const query = `{
      "useCases": *[_type == "useCase" ${filterString}] | order(${sortOrder}) {
        _id,
        title,
        "slug": slug.current,
        excerpt,
        mainImage,
        categories
      }
    }`

    const data = await client.fetch(query)
    return NextResponse.json(data)
  } catch (error) {
    console.error("Error fetching use cases:", error)
    return NextResponse.json({ error: "Failed to fetch use cases", useCases: [] }, { status: 500 })
  }
}
