import { createClient } from "next-sanity"
import { NextRequest, NextResponse } from "next/server"

const client = createClient({
  projectId: process.env.NEXT_PUBLIC_SANITY_PROJECT_ID || process.env.SANITY_PROJECT_ID,
  dataset: process.env.NEXT_PUBLIC_SANITY_DATASET || process.env.SANITY_DATASET || "production",
  apiVersion: "2023-05-03",
  useCdn: false,
  token: process.env.SANITY_API_TOKEN,
})

export async function POST(request: NextRequest) {
  try {
    const { documentId, vote } = await request.json()

    if (!documentId || !["yes", "no"].includes(vote)) {
      return NextResponse.json({ error: "Invalid request" }, { status: 400 })
    }

    const field = vote === "yes" ? "helpfulYes" : "helpfulNo"

    await client
      .patch(documentId)
      .setIfMissing({ [field]: 0 })
      .inc({ [field]: 1 })
      .commit()

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error("Rate API error:", error)
    return NextResponse.json({ error: "Failed to record vote" }, { status: 500 })
  }
}
