"use client"

import { useState } from "react"
import Image from "next/image"
import { urlForImage } from "@/lib/sanity-image"
import { Button } from "@/components/ui/button"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command"
import { ChevronsUpDown, Check, ArrowRightLeft, ShoppingCart, X } from "lucide-react"
import { cn } from "@/lib/utils"

type Product = {
  _id: string
  name: string
  image?: any
  brand?: string
  price?: string
  size?: string
  form?: string
  activeIngredient?: string
  affiliateLink?: string
  OTC?: boolean
  ingredients?: Array<{ _id: string; title: string; slug: string }>
}

type ProductComparisonToolProps = {
  products: Product[]
}

function ProductSelector({
  products,
  selected,
  onSelect,
  label,
}: {
  products: Product[]
  selected: Product | null
  onSelect: (product: Product | null) => void
  label: string
}) {
  const [open, setOpen] = useState(false)

  return (
    <div className="flex-1">
      <label className="block text-sm font-medium text-gray-700 mb-2">{label}</label>
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            role="combobox"
            aria-expanded={open}
            className="w-full justify-between h-auto min-h-[44px] text-left"
          >
            {selected ? (
              <span className="truncate">{selected.name}</span>
            ) : (
              <span className="text-muted-foreground">Search products...</span>
            )}
            <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-[--radix-popover-trigger-width] p-0" align="start">
          <Command>
            <CommandInput placeholder="Search products..." />
            <CommandList>
              <CommandEmpty>No product found.</CommandEmpty>
              <CommandGroup>
                {products.map((product) => (
                  <CommandItem
                    key={product._id}
                    value={product.name}
                    onSelect={() => {
                      onSelect(selected?._id === product._id ? null : product)
                      setOpen(false)
                    }}
                  >
                    <Check
                      className={cn(
                        "mr-2 h-4 w-4",
                        selected?._id === product._id ? "opacity-100" : "opacity-0"
                      )}
                    />
                    <div className="flex flex-col">
                      <span>{product.name}</span>
                      {product.brand && (
                        <span className="text-xs text-muted-foreground">{product.brand}</span>
                      )}
                    </div>
                  </CommandItem>
                ))}
              </CommandGroup>
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>
      {selected && (
        <button
          onClick={() => onSelect(null)}
          className="mt-1 text-xs text-gray-500 hover:text-red-500 flex items-center gap-1"
        >
          <X className="h-3 w-3" /> Clear
        </button>
      )}
    </div>
  )
}

function ComparisonRow({
  label,
  valueA,
  valueB,
}: {
  label: string
  valueA: React.ReactNode
  valueB: React.ReactNode
}) {
  return (
    <tr className="border-b border-gray-100 hover:bg-blue-50/40">
      <td className="p-3 font-medium text-gray-700 bg-gray-50/50 w-1/4">{label}</td>
      <td className="p-3 text-center w-[37.5%]">{valueA || <span className="text-gray-400">-</span>}</td>
      <td className="p-3 text-center w-[37.5%]">{valueB || <span className="text-gray-400">-</span>}</td>
    </tr>
  )
}

export default function ProductComparisonTool({ products }: ProductComparisonToolProps) {
  const [productA, setProductA] = useState<Product | null>(null)
  const [productB, setProductB] = useState<Product | null>(null)
  const [showResults, setShowResults] = useState(false)

  const handleCompare = () => {
    if (productA && productB) {
      setShowResults(true)
    }
  }

  const handleSwap = () => {
    const tempA = productA
    setProductA(productB)
    setProductB(tempA)
  }

  const handleReset = () => {
    setProductA(null)
    setProductB(null)
    setShowResults(false)
  }

  return (
    <div className="medical-card p-6 mb-10">
      <h2 className="text-2xl font-bold mb-2">Compare Products</h2>
      <p className="text-gray-600 mb-6">
        Select two products to see a side-by-side comparison of their key attributes.
      </p>

      <div className="flex flex-col md:flex-row gap-4 items-end mb-6">
        <ProductSelector
          products={products}
          selected={productA}
          onSelect={(p) => {
            setProductA(p)
            setShowResults(false)
          }}
          label="Product A"
        />

        <button
          onClick={handleSwap}
          className="p-2 rounded-full hover:bg-gray-100 transition-colors self-center md:self-end md:mb-1"
          title="Swap products"
        >
          <ArrowRightLeft className="h-5 w-5 text-gray-500" />
        </button>

        <ProductSelector
          products={products}
          selected={productB}
          onSelect={(p) => {
            setProductB(p)
            setShowResults(false)
          }}
          label="Product B"
        />
      </div>

      <div className="flex gap-3">
        <Button
          onClick={handleCompare}
          disabled={!productA || !productB || productA._id === productB._id}
          className="flex-1 md:flex-none"
        >
          Compare
        </Button>
        {showResults && (
          <Button variant="outline" onClick={handleReset}>
            Reset
          </Button>
        )}
      </div>

      {productA && productB && productA._id === productB._id && (
        <p className="text-sm text-amber-600 mt-2">Please select two different products to compare.</p>
      )}

      {showResults && productA && productB && (
        <div className="mt-8 overflow-x-auto">
          <table className="w-full border-collapse rounded-lg overflow-hidden border border-gray-200">
            <thead>
              <tr className="bg-primary/5">
                <th className="p-3 text-left font-semibold text-gray-800 border-b-2 border-primary/20 w-1/4">
                  Attribute
                </th>
                <th className="p-3 text-center font-semibold text-gray-800 border-b-2 border-primary/20 w-[37.5%]">
                  <div className="flex flex-col items-center gap-2">
                    {productA.image && (
                      <div className="relative h-16 w-16">
                        <Image
                          src={urlForImage(productA.image).width(128).height(128).url() || "/placeholder.svg"}
                          alt={productA.name}
                          fill
                          className="object-contain"
                          sizes="64px"
                        />
                      </div>
                    )}
                    <span>{productA.name}</span>
                  </div>
                </th>
                <th className="p-3 text-center font-semibold text-gray-800 border-b-2 border-primary/20 w-[37.5%]">
                  <div className="flex flex-col items-center gap-2">
                    {productB.image && (
                      <div className="relative h-16 w-16">
                        <Image
                          src={urlForImage(productB.image).width(128).height(128).url() || "/placeholder.svg"}
                          alt={productB.name}
                          fill
                          className="object-contain"
                          sizes="64px"
                        />
                      </div>
                    )}
                    <span>{productB.name}</span>
                  </div>
                </th>
              </tr>
            </thead>
            <tbody>
              <ComparisonRow label="Brand" valueA={productA.brand} valueB={productB.brand} />
              <ComparisonRow label="Form" valueA={productA.form} valueB={productB.form} />
              <ComparisonRow
                label="Active Ingredient"
                valueA={productA.activeIngredient}
                valueB={productB.activeIngredient}
              />
              <ComparisonRow label="Price" valueA={productA.price} valueB={productB.price} />
              <ComparisonRow label="Size" valueA={productA.size} valueB={productB.size} />
              <ComparisonRow
                label="OTC Available"
                valueA={
                  productA.OTC != null ? (
                    <span className={productA.OTC ? "text-green-600 font-medium" : "text-red-600"}>
                      {productA.OTC ? "Yes" : "No"}
                    </span>
                  ) : null
                }
                valueB={
                  productB.OTC != null ? (
                    <span className={productB.OTC ? "text-green-600 font-medium" : "text-red-600"}>
                      {productB.OTC ? "Yes" : "No"}
                    </span>
                  ) : null
                }
              />
              <ComparisonRow
                label="Key Ingredients"
                valueA={
                  productA.ingredients && productA.ingredients.length > 0
                    ? productA.ingredients.map((ing) => ing.title).join(", ")
                    : null
                }
                valueB={
                  productB.ingredients && productB.ingredients.length > 0
                    ? productB.ingredients.map((ing) => ing.title).join(", ")
                    : null
                }
              />
              <tr className="border-b border-gray-100">
                <td className="p-3 font-medium text-gray-700 bg-gray-50/50">Buy</td>
                <td className="p-3 text-center">
                  {productA.affiliateLink ? (
                    <a
                      href={productA.affiliateLink}
                      target="_blank"
                      rel="sponsored nofollow noopener"
                      className="inline-flex items-center gap-1.5 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm"
                    >
                      <ShoppingCart className="h-4 w-4" />
                      Check Price
                    </a>
                  ) : (
                    <span className="text-gray-400">-</span>
                  )}
                </td>
                <td className="p-3 text-center">
                  {productB.affiliateLink ? (
                    <a
                      href={productB.affiliateLink}
                      target="_blank"
                      rel="sponsored nofollow noopener"
                      className="inline-flex items-center gap-1.5 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm"
                    >
                      <ShoppingCart className="h-4 w-4" />
                      Check Price
                    </a>
                  ) : (
                    <span className="text-gray-400">-</span>
                  )}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
