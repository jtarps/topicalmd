import { getUseCase, getAllUseCaseSlugs } from "@/lib/sanity"
import PortableTextRenderer from "@/components/portable-text-renderer"
import Image from "next/image"
import { urlForImage } from "@/lib/sanity-image"
import { notFound } from "next/navigation"
import type { Metadata } from "next"
import ProductCard from "@/components/product-card"
import RelatedContent from "@/components/related-content"

type Props = {
  params: Promise<{ slug: string }>
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params
  const useCase = await getUseCase(slug)

  if (!useCase) {
    return {
      title: "Guide Not Found",
      description: "The requested guide could not be found",
    }
  }

  return {
    title: useCase.title,
    description: useCase.excerpt,
  }
}

export async function generateStaticParams() {
  const slugs = await getAllUseCaseSlugs()
  return slugs.map((slug) => ({ slug }))
}

export default async function UseCasePage({ params }: Props) {
  const { slug } = await params
  const useCase = await getUseCase(slug)

  if (!useCase) {
    notFound()
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <article className="max-w-4xl mx-auto">
        <header className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold mb-4">{useCase.title}</h1>
          <p className="text-xl text-gray-600 mb-6">{useCase.excerpt}</p>
          {useCase.mainImage && (
            <div className="relative h-[400px] w-full mb-8">
              <Image
                src={urlForImage(useCase.mainImage).url() || "/placeholder.svg"}
                alt={useCase.title}
                fill
                className="object-cover rounded-lg"
                sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
              />
            </div>
          )}
        </header>

        <PortableTextRenderer value={useCase.introduction} className="prose max-w-none mb-12" />

        {useCase.recommendedProducts && useCase.recommendedProducts.length > 0 && (
          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-6">Recommended Products</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {useCase.recommendedProducts.map((product) => (
                <ProductCard key={product._id} product={product} />
              ))}
            </div>
          </section>
        )}

        <PortableTextRenderer value={useCase.content} className="prose max-w-none mb-12" />

        {useCase.relatedContent && <RelatedContent content={useCase.relatedContent} />}
      </article>
    </div>
  )
}
