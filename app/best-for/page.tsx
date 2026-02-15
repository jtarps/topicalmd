import Link from "next/link"
import { getAllUseCases } from "@/lib/sanity"
import FeaturedCard from "@/components/featured-card"
import type { Metadata } from "next"

export const metadata: Metadata = {
  title: "Best For Guides - TopicalMD",
  description: "Find the best topical treatments for specific conditions and use cases.",
}

export default async function BestForPage() {
  const useCases = await getAllUseCases()

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="medical-breadcrumb">
        <Link href="/" className="medical-breadcrumb-item">
          Home
        </Link>
        <span className="medical-breadcrumb-separator">/</span>
        <span className="font-medium">Best For Guides</span>
      </div>

      <h1 className="text-3xl font-bold mb-6 text-primary">Best For Guides</h1>

      <div className="medical-info mb-8">
        <p>
          Our "Best For" guides help you find the most effective topical treatments for specific conditions and needs.
          Each guide is researched and reviewed by healthcare professionals.
        </p>
      </div>

      {useCases.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <p className="text-xl text-gray-600">No guides found</p>
          <p className="mt-2 text-gray-500">Check back soon for new condition guides</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {useCases.map((useCase) => (
            <FeaturedCard
              key={useCase._id}
              title={useCase.title}
              description={useCase.excerpt}
              image={useCase.mainImage}
              slug={`/best-for/${useCase.slug}`}
            />
          ))}
        </div>
      )}
    </div>
  )
}
