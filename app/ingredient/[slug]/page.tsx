import { getIngredient, getAllIngredientSlugs } from "@/lib/sanity"
import PortableTextRenderer from "@/components/portable-text-renderer"
import Image from "next/image"
import { urlForImage } from "@/lib/sanity-image"
import { notFound } from "next/navigation"
import type { Metadata } from "next"
import RelatedContent from "@/components/related-content"

type Props = {
  params: Promise<{ slug: string }>
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params
  const ingredient = await getIngredient(slug)

  if (!ingredient) {
    return {
      title: "Ingredient Not Found",
      description: "The requested ingredient could not be found",
    }
  }

  return {
    title: `${ingredient.title} - Ingredient Guide`,
    description: ingredient.excerpt,
  }
}

export async function generateStaticParams() {
  const slugs = await getAllIngredientSlugs()
  return slugs.map((slug) => ({ slug }))
}

export default async function IngredientPage({ params }: Props) {
  const { slug } = await params
  const ingredient = await getIngredient(slug)

  if (!ingredient) {
    notFound()
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <article className="max-w-4xl mx-auto">
        <header className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold mb-4">{ingredient.title}</h1>
          <p className="text-xl text-gray-600 mb-6">{ingredient.excerpt}</p>
          {ingredient.mainImage && (
            <div className="relative h-[400px] w-full mb-8">
              <Image
                src={urlForImage(ingredient.mainImage).url() || "/placeholder.svg"}
                alt={ingredient.title}
                fill
                className="object-cover rounded-lg"
                sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
              />
            </div>
          )}
        </header>

        <div className="grid md:grid-cols-3 gap-8">
          <div className="md:col-span-2">
            <PortableTextRenderer value={ingredient.content} />
          </div>

          <aside className="md:col-span-1">
            <div className="bg-gray-50 p-6 rounded-lg border border-gray-200 mb-6">
              <h3 className="text-lg font-bold mb-4">Quick Facts</h3>
              <dl className="space-y-2">
                {ingredient.scientificName && (
                  <>
                    <dt className="text-sm font-medium text-gray-500">Scientific Name</dt>
                    <dd className="text-gray-900">{ingredient.scientificName}</dd>
                  </>
                )}
                {ingredient.origin && (
                  <>
                    <dt className="text-sm font-medium text-gray-500">Origin</dt>
                    <dd className="text-gray-900">{ingredient.origin}</dd>
                  </>
                )}
                {ingredient.category && (
                  <>
                    <dt className="text-sm font-medium text-gray-500">Category</dt>
                    <dd className="text-gray-900">{ingredient.category}</dd>
                  </>
                )}
              </dl>
            </div>

            {ingredient.benefits && ingredient.benefits.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-bold mb-2">Benefits</h3>
                <ul className="list-disc pl-5 space-y-1">
                  {ingredient.benefits.map((benefit, index) => (
                    <li key={index} className="text-gray-700">
                      {benefit}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {ingredient.sideEffects && ingredient.sideEffects.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-bold mb-2">Potential Side Effects</h3>
                <ul className="list-disc pl-5 space-y-1">
                  {ingredient.sideEffects.map((sideEffect, index) => (
                    <li key={index} className="text-gray-700">
                      {sideEffect}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </aside>
        </div>

        {ingredient.relatedContent && <RelatedContent content={ingredient.relatedContent} />}
      </article>
    </div>
  )
}
