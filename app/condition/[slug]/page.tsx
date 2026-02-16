import { getUseCasesByCategory } from "@/lib/sanity"
import { notFound } from "next/navigation"
import type { Metadata } from "next"
import Link from "next/link"
import Image from "next/image"
import { urlForImage } from "@/lib/sanity-image"
import FeaturedCard from "@/components/featured-card"
import ProductCard from "@/components/product-card"
import { ArrowRight } from "lucide-react"

const CATEGORIES: Record<string, { title: string; description: string }> = {
  arthritis: {
    title: "Arthritis Pain Relief",
    description:
      "Expert-reviewed topical treatments for arthritis, including creams, gels, and patches that target joint inflammation and stiffness.",
  },
  "muscle-pain": {
    title: "Muscle Pain Relief",
    description:
      "Find the best topical solutions for sore muscles, strains, and tension. Compare muscle rubs, creams, and patches backed by evidence.",
  },
  "joint-pain": {
    title: "Joint Pain Relief",
    description:
      "Discover topical treatments designed to address joint pain and discomfort. Reviews and comparisons to help you choose the right product.",
  },
  "neuropathic-pain": {
    title: "Neuropathic Pain Relief",
    description:
      "Topical options for nerve-related pain conditions including diabetic neuropathy and post-herpetic neuralgia. Evidence-based reviews and guides.",
  },
  inflammation: {
    title: "Anti-Inflammatory Treatments",
    description:
      "Explore topical anti-inflammatory treatments including NSAIDs, natural alternatives, and combination products for reducing swelling and pain.",
  },
}

type Props = {
  params: Promise<{ slug: string }>
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params
  const category = CATEGORIES[slug]

  if (!category) {
    return { title: "Condition Not Found" }
  }

  return {
    title: `${category.title} - TopicalMD`,
    description: category.description,
  }
}

export function generateStaticParams() {
  return Object.keys(CATEGORIES).map((slug) => ({ slug }))
}

export default async function ConditionPage({ params }: Props) {
  const { slug } = await params
  const category = CATEGORIES[slug]

  if (!category) {
    notFound()
  }

  const data = await getUseCasesByCategory(slug)

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="medical-breadcrumb">
        <Link href="/" className="medical-breadcrumb-item">
          Home
        </Link>
        <span className="medical-breadcrumb-separator">/</span>
        <span className="font-medium">{category.title}</span>
      </div>

      <header className="mb-10">
        <h1 className="text-3xl md:text-4xl font-bold mb-4 text-primary">{category.title}</h1>
        <p className="text-xl text-gray-600 max-w-3xl">{category.description}</p>
      </header>

      {/* Guides for this condition */}
      {data.useCases && data.useCases.length > 0 && (
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-6">Guides &amp; Best-For Articles</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {data.useCases.map((uc: any) => (
              <FeaturedCard
                key={uc._id}
                title={uc.title}
                description={uc.excerpt}
                image={uc.mainImage}
                slug={`/best-for/${uc.slug}`}
              />
            ))}
          </div>
        </section>
      )}

      {/* Related products */}
      {data.relatedProducts && data.relatedProducts.length > 0 && (
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-6">Related Products</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {data.relatedProducts.map((product: any) => (
              <ProductCard key={product._id} product={product} />
            ))}
          </div>
        </section>
      )}

      {/* Related reviews */}
      {data.relatedReviews && data.relatedReviews.length > 0 && (
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-6">Product Reviews</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {data.relatedReviews.map((review: any) => (
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

      {/* Empty state */}
      {(!data.useCases || data.useCases.length === 0) &&
        (!data.relatedProducts || data.relatedProducts.length === 0) &&
        (!data.relatedReviews || data.relatedReviews.length === 0) && (
          <div className="text-center py-16 bg-gray-50 rounded-lg">
            <p className="text-xl text-gray-600 mb-2">
              No content found for {category.title.toLowerCase()} yet.
            </p>
            <p className="text-gray-500 mb-6">
              Check back soon as we are continually adding new reviews and guides.
            </p>
            <Link
              href="/reviews"
              className="inline-flex items-center gap-2 text-primary hover:underline font-medium"
            >
              Browse all reviews <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        )}

      {/* Browse other conditions */}
      <section className="mt-12 pt-8 border-t border-gray-200">
        <h2 className="text-xl font-bold mb-4">Browse Other Conditions</h2>
        <div className="flex flex-wrap gap-3">
          {Object.entries(CATEGORIES)
            .filter(([key]) => key !== slug)
            .map(([key, cat]) => (
              <Link
                key={key}
                href={`/condition/${key}`}
                className="px-4 py-2 bg-blue-50 text-primary rounded-full text-sm font-medium hover:bg-blue-100 transition-colors"
              >
                {cat.title}
              </Link>
            ))}
        </div>
      </section>
    </div>
  )
}
