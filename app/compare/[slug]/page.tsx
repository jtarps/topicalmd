import { getComparison, getAllComparisonSlugs } from "@/lib/sanity"
import { PortableText } from "@portabletext/react"
import Image from "next/image"
import { urlForImage } from "@/lib/sanity-image"
import { notFound } from "next/navigation"
import type { Metadata } from "next"
import ComparisonTable from "@/components/comparison-table"
import RelatedContent from "@/components/related-content"
import ProductCard from "@/components/product-card"

type Props = {
  params: Promise<{ slug: string }>
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params
  const comparison = await getComparison(slug)

  if (!comparison) {
    return {
      title: "Comparison Not Found",
      description: "The requested comparison could not be found",
    }
  }

  return {
    title: comparison.title,
    description: comparison.excerpt,
  }
}

export async function generateStaticParams() {
  const slugs = await getAllComparisonSlugs()
  return slugs.map((slug) => ({ slug }))
}

export default async function ComparisonPage({ params }: Props) {
  const { slug } = await params
  const comparison = await getComparison(slug)

  if (!comparison) {
    notFound()
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <article className="max-w-4xl mx-auto">
        <header className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold mb-4">{comparison.title}</h1>
          <p className="text-xl text-gray-600 mb-6">{comparison.excerpt}</p>
          {comparison.mainImage && (
            <div className="relative h-[400px] w-full mb-8">
              <Image
                src={urlForImage(comparison.mainImage).url() || "/placeholder.svg"}
                alt={comparison.title}
                fill
                className="object-cover rounded-lg"
                sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
              />
            </div>
          )}
        </header>

        <div className="prose max-w-none mb-12">
          <PortableText value={comparison.introduction} />
        </div>

        {comparison.products && comparison.products.length > 0 && (
          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-6">Head-to-Head Comparison</h2>
            <ComparisonTable products={comparison.products} criteria={comparison.criteria} />
            
            {/* Product Cards with Affiliate Links */}
            <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
              {comparison.products.map((product) => (
                <ProductCard
                  key={product._id || product.name}
                  product={{
                    _id: product._id || product.name,
                    name: product.name,
                    image: product.image,
                    price: product.price,
                    affiliateLink: product.affiliateLink,
                  }}
                />
              ))}
            </div>
          </section>
        )}

        <div className="prose max-w-none mb-12">
          <PortableText value={comparison.content} />
        </div>

        {comparison.winner && (
          <section className="mb-12 p-6 bg-green-50 rounded-lg border border-green-200">
            <h2 className="text-2xl font-bold mb-4">Our Verdict</h2>
            <div className="flex items-center gap-4">
              {comparison.winner.image && (
                <div className="relative h-24 w-24 flex-shrink-0">
                  <Image
                    src={urlForImage(comparison.winner.image).url() || "/placeholder.svg"}
                    alt={comparison.winner.name}
                    fill
                    className="object-contain"
                  />
                </div>
              )}
              <div>
                <h3 className="text-xl font-bold">{comparison.winner.name}</h3>
                <p className="text-gray-700">{comparison.winnerReason}</p>
              </div>
            </div>
          </section>
        )}

        {comparison.relatedContent && <RelatedContent content={comparison.relatedContent} />}
      </article>
    </div>
  )
}
