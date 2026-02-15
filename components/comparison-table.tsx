import Image from "next/image"
import { urlForImage } from "@/lib/sanity-image"
import { Check, X, ShoppingCart } from "lucide-react"
import Link from "next/link"

type ComparisonTableProps = {
  products: Array<{
    _id: string
    name: string
    image?: any
    price?: string
    affiliateLink?: string
    brand?: string
    size?: string
    values: Record<string, any>
  }>
  criteria: Array<{
    _id: string
    name: string
    key: string
    type: "text" | "number" | "boolean" | "rating"
  }>
}

export default function ComparisonTable({ products, criteria }: ComparisonTableProps) {
  if (!products || products.length === 0 || !criteria || criteria.length === 0) {
    return null
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse">
        <thead>
          <tr className="bg-gray-50">
            <th className="p-4 text-left border"></th>
            {products.map((product) => (
              <th key={product._id} className="p-4 text-center border">
                <div className="flex flex-col items-center space-y-2">
                  {product.image && (
                    <div className="relative h-16 w-16 mx-auto">
                      <Image
                        src={urlForImage(product.image).url() || "/placeholder.svg"}
                        alt={product.name}
                        fill
                        className="object-contain"
                        sizes="64px"
                      />
                    </div>
                  )}
                  <span className="font-medium">{product.name}</span>
                  {product.brand && <span className="text-xs text-gray-500">{product.brand}</span>}
                  {product.price && <span className="text-sm text-gray-600">{product.price}</span>}
                  {product.affiliateLink && (
                    <a
                      href={product.affiliateLink}
                      target="_blank"
                      rel="sponsored nofollow noopener"
                      className="mt-2 flex items-center justify-center gap-1 px-3 py-1.5 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                    >
                      <ShoppingCart className="h-3 w-3" />
                      Check Price
                    </a>
                  )}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {criteria.map((criterion) => (
            <tr key={criterion._id} className="border-t hover:bg-gray-50">
              <td className="p-4 font-medium border">{criterion.name}</td>
              {products.map((product) => (
                <td key={`${product._id}-${criterion._id}`} className="p-4 text-center border">
                  {renderValue(product.values[criterion.key], criterion.type)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function renderValue(value: any, type: string) {
  if (value === undefined || value === null) {
    return <span className="text-gray-400">-</span>
  }

  switch (type) {
    case "boolean":
      return value ? (
        <Check className="h-5 w-5 text-green-600 mx-auto" />
      ) : (
        <X className="h-5 w-5 text-red-600 mx-auto" />
      )
    case "rating":
      return (
        <div className="flex justify-center">
          <span className="font-medium">{value}/5</span>
        </div>
      )
    default:
      return <span>{value}</span>
  }
}
