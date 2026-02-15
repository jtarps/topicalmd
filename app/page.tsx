import Link from "next/link"
import { getHomepageData } from "@/lib/sanity"
import FeaturedCard from "@/components/featured-card"
import type { Metadata } from "next"
import { AlertTriangle, BookOpen, Search, ThumbsUp, Pill } from "lucide-react"
import EmptyState from "@/components/empty-state"

export const metadata: Metadata = {
  title: "TopicalMD - Expert Reviews & Information on Topical Treatments",
  description:
    "Your trusted medical resource for ointments, pain creams, balms, and topical treatments with expert reviews, comparisons, and ingredient analysis.",
}

export default async function Home() {
  const { featuredReviews, featuredUseCases, featuredComparisons, featuredIngredients, featuredFaqs } =
    await getHomepageData()

  const hasContent =
    (featuredReviews && featuredReviews.length > 0) ||
    (featuredUseCases && featuredUseCases.length > 0) ||
    (featuredComparisons && featuredComparisons.length > 0) ||
    (featuredIngredients && featuredIngredients.length > 0) ||
    (featuredFaqs && featuredFaqs.length > 0)

  return (
    <div className="bg-gray-50">
      <div className="bg-primary text-white py-16">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto text-center">
            <h1 className="text-4xl md:text-5xl font-bold mb-4">Your Trusted Guide to Topical Treatments</h1>
            <p className="text-xl opacity-90 mb-8">
              Evidence-based information on ointments, creams, and balms for pain relief and skin conditions
            </p>
            <div className="relative max-w-xl mx-auto">
              <form action="/search" method="get">
                <div className="flex">
                  <input
                    type="text"
                    name="q"
                    placeholder="Search conditions, treatments, ingredients..."
                    className="w-full px-4 py-3 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-white/50"
                    required
                  />
                  <button
                    type="submit"
                    className="bg-white text-primary px-6 rounded-r-lg hover:bg-gray-100 transition-colors"
                  >
                    <Search className="h-5 w-5" />
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <div className="medical-card p-6 flex flex-col items-center text-center">
            <div className="bg-blue-100 p-3 rounded-full mb-4">
              <ThumbsUp className="h-8 w-8 text-primary" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Expert-Reviewed</h3>
            <p className="text-gray-600">
              All content is reviewed by our medical advisory board to ensure accuracy and reliability.
            </p>
          </div>
          <div className="medical-card p-6 flex flex-col items-center text-center">
            <div className="bg-blue-100 p-3 rounded-full mb-4">
              <BookOpen className="h-8 w-8 text-primary" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Evidence-Based</h3>
            <p className="text-gray-600">Our recommendations are based on clinical studies and scientific research.</p>
          </div>
          <div className="medical-card p-6 flex flex-col items-center text-center">
            <div className="bg-blue-100 p-3 rounded-full mb-4">
              <Pill className="h-8 w-8 text-primary" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Comprehensive</h3>
            <p className="text-gray-600">
              Detailed information on ingredients, side effects, and effectiveness for informed decisions.
            </p>
          </div>
        </div>

        <div className="medical-info mb-8">
          <div className="flex items-start">
            <AlertTriangle className="h-6 w-6 mr-3 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-medium mb-1">Medical Disclaimer</h4>
              <p className="text-sm">
                The information provided on this site is for educational purposes only and is not intended as medical
                advice. Always consult with a healthcare professional before using any topical treatments.
              </p>
            </div>
          </div>
        </div>

        {!hasContent && (
          <EmptyState
            title="Content Coming Soon"
            message="We're currently working on adding expert-reviewed content to our database. Check back soon for reviews, guides, and more!"
          />
        )}

        {featuredReviews && featuredReviews.length > 0 && (
          <section className="mb-12">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-primary">Featured Reviews</h2>
              <Link href="/reviews" className="text-primary hover:underline font-medium">
                View all reviews
              </Link>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {featuredReviews.map((review) => (
                <FeaturedCard
                  key={review._id}
                  title={review.title}
                  description={review.excerpt}
                  image={review.mainImage}
                  slug={`/review/${review.slug}`}
                />
              ))}
            </div>
          </section>
        )}

        {featuredUseCases && featuredUseCases.length > 0 && (
          <section className="mb-12">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-primary">Best For Guides</h2>
              <Link href="/best-for" className="text-primary hover:underline font-medium">
                View all guides
              </Link>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {featuredUseCases.map((useCase) => (
                <FeaturedCard
                  key={useCase._id}
                  title={useCase.title}
                  description={useCase.excerpt}
                  image={useCase.mainImage}
                  slug={`/best-for/${useCase.slug}`}
                />
              ))}
            </div>
          </section>
        )}

        {featuredComparisons && featuredComparisons.length > 0 && (
          <section className="mb-12">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-primary">Product Comparisons</h2>
              <Link href="/compare" className="text-primary hover:underline font-medium">
                View all comparisons
              </Link>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {featuredComparisons.map((comparison) => (
                <FeaturedCard
                  key={comparison._id}
                  title={comparison.title}
                  description={comparison.excerpt}
                  image={comparison.mainImage}
                  slug={`/compare/${comparison.slug}`}
                />
              ))}
            </div>
          </section>
        )}

        {(featuredIngredients && featuredIngredients.length > 0) || (featuredFaqs && featuredFaqs.length > 0) ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {featuredIngredients && featuredIngredients.length > 0 && (
              <section>
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-primary">Ingredient Guides</h2>
                  <Link href="/ingredient" className="text-primary hover:underline font-medium">
                    View all ingredients
                  </Link>
                </div>
                <div className="grid grid-cols-1 gap-4">
                  {featuredIngredients.map((ingredient) => (
                    <FeaturedCard
                      key={ingredient._id}
                      title={ingredient.title}
                      description={ingredient.excerpt}
                      image={ingredient.mainImage}
                      slug={`/ingredient/${ingredient.slug}`}
                      variant="horizontal"
                    />
                  ))}
                </div>
              </section>
            )}

            {featuredFaqs && featuredFaqs.length > 0 && (
              <section>
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-primary">Frequently Asked Questions</h2>
                  <Link href="/faq" className="text-primary hover:underline font-medium">
                    View all FAQs
                  </Link>
                </div>
                <div className="grid grid-cols-1 gap-4">
                  {featuredFaqs.map((faq) => (
                    <FeaturedCard
                      key={faq._id}
                      title={faq.title}
                      description={faq.excerpt}
                      slug={`/faq/${faq.slug}`}
                      variant="horizontal"
                    />
                  ))}
                </div>
              </section>
            )}
          </div>
        ) : null}
      </div>
    </div>
  )
}
