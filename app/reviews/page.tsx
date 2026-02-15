import Link from "next/link"
import { getAllReviews } from "@/lib/sanity"
import FeaturedCard from "@/components/featured-card"
import type { Metadata } from "next"

export const metadata: Metadata = {
  title: "Product Reviews - TopicalMD",
  description: "Expert reviews of ointments, pain creams, balms, and topical treatments.",
}

export default async function ReviewsPage() {
  const reviews = await getAllReviews()

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="medical-breadcrumb">
        <Link href="/" className="medical-breadcrumb-item">
          Home
        </Link>
        <span className="medical-breadcrumb-separator">/</span>
        <span className="font-medium">Reviews</span>
      </div>

      <h1 className="text-3xl font-bold mb-6 text-primary">Product Reviews</h1>

      <div className="medical-info mb-8">
        <p>
          Our reviews are based on clinical research, expert analysis, and real user experiences. Each product is
          thoroughly evaluated for effectiveness, safety, and value.
        </p>
      </div>

      {reviews.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <p className="text-xl text-gray-600">No reviews found</p>
          <p className="mt-2 text-gray-500">Check back soon for new product reviews</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {reviews.map((review) => (
            <FeaturedCard
              key={review._id}
              title={review.title}
              description={review.excerpt}
              image={review.mainImage}
              slug={`/review/${review.slug}`}
            />
          ))}
        </div>
      )}
    </div>
  )
}
