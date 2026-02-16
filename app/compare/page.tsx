import Link from "next/link"
import { getAllComparisons, getAllProducts } from "@/lib/sanity"
import FeaturedCard from "@/components/featured-card"
import ProductComparisonTool from "@/components/product-comparison-tool"
import type { Metadata } from "next"

export const metadata: Metadata = {
  title: "Product Comparisons - TopicalMD",
  description: "Head-to-head comparisons of topical treatments to help you choose the right product.",
}

export default async function ComparisonsPage() {
  const [comparisons, products] = await Promise.all([getAllComparisons(), getAllProducts()])

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="medical-breadcrumb">
        <Link href="/" className="medical-breadcrumb-item">
          Home
        </Link>
        <span className="medical-breadcrumb-separator">/</span>
        <span className="font-medium">Comparisons</span>
      </div>

      <h1 className="text-3xl font-bold mb-6 text-primary">Product Comparisons</h1>

      <div className="medical-info mb-8">
        <p>
          Our head-to-head comparisons help you understand the differences between similar products so you can make an
          informed decision about which treatment is right for your needs.
        </p>
      </div>

      {products && products.length >= 2 && <ProductComparisonTool products={products} />}

      {comparisons.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <p className="text-xl text-gray-600">No comparisons found</p>
          <p className="mt-2 text-gray-500">Check back soon for new product comparisons</p>
        </div>
      ) : (
        <>
          <h2 className="text-2xl font-bold mb-6">Detailed Comparison Articles</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {comparisons.map((comparison) => (
              <FeaturedCard
                key={comparison._id}
                title={comparison.title}
                description={comparison.excerpt}
                image={comparison.mainImage}
                slug={`/compare/${comparison.slug}`}
              />
            ))}
          </div>
        </>
      )}
    </div>
  )
}
