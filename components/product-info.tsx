import Image from "next/image"
import { urlForImage } from "@/lib/sanity-image"
import { ShoppingCart, Shield } from "lucide-react"

type ProductInfoProps = {
  product: {
    name: string
    image?: any
    price?: string
    affiliateLink?: string
    brand?: string
    size?: string
  }
}

export default function ProductInfo({ product }: ProductInfoProps) {
  if (!product) return null

  return (
    <div className="medical-card mb-6">
      <div className="medical-header flex items-center justify-between">
        <span>Product Information</span>
      </div>
      <div className="p-4">
        <div className="flex items-center space-x-4 mb-4">
          {product.image && (
            <div className="relative h-20 w-20 flex-shrink-0">
              <Image
                src={urlForImage(product.image).url() || "/placeholder.svg"}
                alt={product.name}
                fill
                className="object-contain"
                sizes="80px"
              />
            </div>
          )}
          <h3 className="text-lg font-bold">{product.name}</h3>
        </div>

        <dl className="space-y-2 mb-4">
          {product.brand && (
            <div className="flex justify-between">
              <dt className="text-sm font-medium text-gray-500">Brand</dt>
              <dd className="text-gray-900">{product.brand}</dd>
            </div>
          )}
          {product.size && (
            <div className="flex justify-between">
              <dt className="text-sm font-medium text-gray-500">Size</dt>
              <dd className="text-gray-900">{product.size}</dd>
            </div>
          )}
          {product.price && (
            <div className="flex justify-between">
              <dt className="text-sm font-medium text-gray-500">Price</dt>
              <dd className="text-gray-900 font-medium">{product.price}</dd>
            </div>
          )}
        </dl>

        {product.affiliateLink && (
          <div className="space-y-2">
            <a
              href={product.affiliateLink}
              target="_blank"
              rel="sponsored nofollow noopener"
              className="flex items-center justify-center w-full py-2 px-4 bg-primary text-white rounded-md hover:bg-primary/90 transition-colors"
            >
              <ShoppingCart className="mr-2 h-4 w-4" /> Check Price on Amazon
            </a>
            <p className="text-xs text-center text-gray-500">
              <Shield className="inline h-3 w-3 mr-1" /> Affiliate link - we may earn a commission
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
