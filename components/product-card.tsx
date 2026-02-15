import Link from "next/link"
import Image from "next/image"
import { urlForImage } from "@/lib/sanity-image"
import RatingStars from "./rating-stars"
import { ShoppingCart } from "lucide-react"

type ProductCardProps = {
  product: {
    _id: string
    name: string
    image?: any
    price?: string
    rating?: number
    slug?: string
    excerpt?: string
    affiliateLink?: string
  }
}

export default function ProductCard({ product }: ProductCardProps) {
  return (
    <div className="rounded-lg border overflow-hidden hover:shadow-md transition-shadow">
      {product.image && (
        <div className="relative h-48 w-full">
          <Image
            src={urlForImage(product.image).width(400).height(300).url() || "/placeholder.svg"}
            alt={product.name}
            fill
            className="object-contain p-4"
            sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
          />
        </div>
      )}
      <div className="p-4">
        <h3 className="font-medium">{product.name}</h3>

        {product.rating && (
          <div className="flex items-center mt-2">
            <RatingStars rating={product.rating} />
            <span className="ml-2 text-sm text-gray-600">{product.rating}/5</span>
          </div>
        )}

        {product.price && <p className="mt-2 font-medium">{product.price}</p>}

        {product.excerpt && <p className="text-sm text-gray-600 mt-2 line-clamp-2">{product.excerpt}</p>}

        <div className="mt-4 flex flex-col gap-2">
          {product.slug && (
            <Link href={`/review/${product.slug}`} className="text-blue-600 hover:underline text-sm">
              Read Review
            </Link>
          )}
          {product.affiliateLink && (
            <a
              href={product.affiliateLink}
              target="_blank"
              rel="sponsored nofollow noopener"
              className="flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm"
            >
              <ShoppingCart className="h-4 w-4" />
              Check Price on Amazon
            </a>
          )}
        </div>
      </div>
    </div>
  )
}
