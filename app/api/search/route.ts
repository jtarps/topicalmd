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
  const query = searchParams.get("q")
  const type = searchParams.get("type") || "all"
  const page = Number.parseInt(searchParams.get("page") || "1")
  const pageSize = Number.parseInt(searchParams.get("pageSize") || "10")

  if (!query) {
    return NextResponse.json({ error: "Query parameter is required", results: [], total: 0 }, { status: 400 })
  }

  try {
    let filter = ""

    // Filter by content type if specified
    if (type !== "all") {
      filter = `&& _type == "${type}"`
    }

    // Build the GROQ query
    const groqQuery = `{
      "total": count(*[_type in ["review", "useCase", "comparison", "ingredient", "faq"] ${filter} && 
        (title match "*${query}*" || 
         excerpt match "*${query}*" || 
         content[].children[].text match "*${query}*" ||
         answer[].children[].text match "*${query}*")]),
      "results": *[_type in ["review", "useCase", "comparison", "ingredient", "faq"] ${filter} && 
        (title match "*${query}*" || 
         excerpt match "*${query}*" || 
         content[].children[].text match "*${query}*" ||
         answer[].children[].text match "*${query}*")]
      | order(_createdAt desc)
      [${(page - 1) * pageSize}...${page * pageSize}] {
        _id,
        _type,
        title,
        "slug": slug.current,
        excerpt,
        mainImage,
        _createdAt
      }
    }`

    const response = await client.fetch(groqQuery)
    return NextResponse.json(response)
  } catch (error) {
    console.error("Search error:", error)
    return NextResponse.json({ error: "Failed to perform search", results: [], total: 0 }, { status: 500 })
  }
}
