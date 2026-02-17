import { getReview, getAllReviewSlugs } from "@/lib/sanity"
import PortableTextRenderer from "@/components/portable-text-renderer"
import Image from "next/image"
import { urlForImage } from "@/lib/sanity-image"
import { notFound } from "next/navigation"
import type { Metadata } from "next"
import RatingStars from "@/components/rating-stars"
import ProductInfo from "@/components/product-info"
import RelatedContent from "@/components/related-content"
import ArticleRating from "@/components/article-rating"
import { AlertTriangle, CheckCircle, XCircle, Info } from "lucide-react"
import Link from "next/link"

type Props = {
  params: Promise<{ slug: string }>
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params
  const review = await getReview(slug)

  if (!review) {
    return {
      title: "Review Not Found",
      description: "The requested review could not be found",
    }
  }

  return {
    title: `${review.title} Review - TopicalMD`,
    description: review.excerpt,
  }
}

export async function generateStaticParams() {
  const slugs = await getAllReviewSlugs()
  return slugs.map((slug) => ({ slug }))
}

export default async function ReviewPage({ params }: Props) {
  const { slug } = await params
  const review = await getReview(slug)

  if (!review) {
    notFound()
  }

  const reviewSchema = {
    "@context": "https://schema.org",
    "@type": "Review",
    name: review.title,
    reviewBody: review.excerpt,
    reviewRating: {
      "@type": "Rating",
      ratingValue: review.rating,
      bestRating: 5,
    },
    author: {
      "@type": "Organization",
      name: "TopicalMD Editorial Team",
    },
    itemReviewed: review.product
      ? {
          "@type": "Product",
          name: review.product.name,
          brand: review.product.brand ? { "@type": "Brand", name: review.product.brand } : undefined,
          offers: review.product.price
            ? {
                "@type": "Offer",
                price: review.product.price.replace(/[^0-9.]/g, ""),
                priceCurrency: "USD",
                url: review.product.affiliateLink || undefined,
              }
            : undefined,
        }
      : undefined,
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(reviewSchema) }}
      />
      <div className="medical-breadcrumb">
        <Link href="/" className="medical-breadcrumb-item">
          Home
        </Link>
        <span className="medical-breadcrumb-separator">/</span>
        <Link href="/reviews" className="medical-breadcrumb-item">
          Reviews
        </Link>
        <span className="medical-breadcrumb-separator">/</span>
        <span className="font-medium">{review.title}</span>
      </div>

      <article className="max-w-4xl mx-auto">
        <header className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold mb-4 text-primary">{review.title}</h1>
          <div className="flex items-center mb-4">
            <RatingStars rating={review.rating} />
            <span className="ml-2 text-gray-600">{review.rating}/5</span>
          </div>
          <div className="medical-info mb-6">
            <div className="flex items-start">
              <Info className="h-5 w-5 mr-2 flex-shrink-0 mt-0.5" />
              <p className="text-lg">{review.excerpt}</p>
            </div>
          </div>
          {review.mainImage && (
            <div className="relative h-[400px] w-full mb-8">
              <Image
                src={urlForImage(review.mainImage).url() || "/placeholder.svg"}
                alt={review.title}
                fill
                className="object-cover rounded-lg"
                sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
              />
            </div>
          )}
        </header>

        <div className="grid md:grid-cols-3 gap-8">
          <div className="md:col-span-2">
            <PortableTextRenderer value={review.content} />

            <div className="medical-warning mt-8">
              <div className="flex items-start">
                <AlertTriangle className="h-5 w-5 mr-2 flex-shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-medium mb-1">Medical Disclaimer</h4>
                  <p className="text-sm">
                    This review is based on available research and expert opinion. Individual results may vary. Consult
                    with a healthcare professional before using any topical treatment, especially if you have existing
                    medical conditions or are taking other medications.
                  </p>
                </div>
              </div>
            </div>

            <div className="mt-8">
              <ArticleRating
                documentId={review._id}
                initialYes={review.helpfulYes || 0}
                initialNo={review.helpfulNo || 0}
              />
            </div>
          </div>

          <aside className="md:col-span-1">
            <ProductInfo product={review.product} />

            {review.pros && review.pros.length > 0 && (
              <div className="medical-card p-4 mb-6">
                <h3 className="text-lg font-bold mb-2 flex items-center">
                  <CheckCircle className="h-5 w-5 text-green-600 mr-2" />
                  Pros
                </h3>
                <ul className="space-y-2">
                  {review.pros.map((pro, index) => (
                    <li key={index} className="flex items-start">
                      <CheckCircle className="h-4 w-4 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                      <span>{pro}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {review.cons && review.cons.length > 0 && (
              <div className="medical-card p-4 mb-6">
                <h3 className="text-lg font-bold mb-2 flex items-center">
                  <XCircle className="h-5 w-5 text-red-600 mr-2" />
                  Cons
                </h3>
                <ul className="space-y-2">
                  {review.cons.map((con, index) => (
                    <li key={index} className="flex items-start">
                      <XCircle className="h-4 w-4 text-red-600 mr-2 mt-0.5 flex-shrink-0" />
                      <span>{con}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div className="medical-card p-4">
              <h3 className="text-lg font-bold mb-2">About This Review</h3>
              <p className="text-sm text-gray-600 mb-4">
                Reviewed by the TopicalMD Editorial Team. Last updated: {new Date().toLocaleDateString("en-US", { month: "long", year: "numeric" })}.
              </p>
              <div className="flex items-center">
                <div className="w-12 h-12 rounded-full bg-blue-100 mr-3 flex items-center justify-center text-blue-600 font-bold text-sm">
                  TMD
                </div>
                <div>
                  <p className="font-medium">TopicalMD Editorial Team</p>
                  <p className="text-sm text-gray-600">Evidence-based health content</p>
                </div>
              </div>
            </div>
          </aside>
        </div>

        {review.relatedContent && <RelatedContent content={review.relatedContent} />}
      </article>
    </div>
  )
}
