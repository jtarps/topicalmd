import Link from "next/link"
import { getAllIngredients } from "@/lib/sanity"
import FeaturedCard from "@/components/featured-card"
import type { Metadata } from "next"

export const metadata: Metadata = {
  title: "Ingredient Guides - TopicalMD",
  description: "Learn about active ingredients in topical treatments, their benefits, and potential side effects.",
}

export default async function IngredientsPage() {
  const ingredients = await getAllIngredients()

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="medical-breadcrumb">
        <Link href="/" className="medical-breadcrumb-item">
          Home
        </Link>
        <span className="medical-breadcrumb-separator">/</span>
        <span className="font-medium">Ingredients</span>
      </div>

      <h1 className="text-3xl font-bold mb-6 text-primary">Ingredient Guides</h1>

      <div className="medical-info mb-8">
        <p>
          Our ingredient guides provide detailed information about active ingredients found in topical treatments,
          including their mechanisms of action, benefits, and potential side effects.
        </p>
      </div>

      {ingredients.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <p className="text-xl text-gray-600">No ingredient guides found</p>
          <p className="mt-2 text-gray-500">Check back soon for new ingredient information</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {ingredients.map((ingredient) => (
            <FeaturedCard
              key={ingredient._id}
              title={ingredient.title}
              description={ingredient.excerpt}
              image={ingredient.mainImage}
              slug={`/ingredient/${ingredient.slug}`}
            />
          ))}
        </div>
      )}
    </div>
  )
}
