import { getFaq, getAllFaqSlugs } from "@/lib/sanity"
import PortableTextRenderer from "@/components/portable-text-renderer"
import { notFound } from "next/navigation"
import type { Metadata } from "next"
import RelatedContent from "@/components/related-content"
import RelatedFaqs from "@/components/related-faqs"

type Props = {
  params: Promise<{ slug: string }>
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params
  const faq = await getFaq(slug)

  if (!faq) {
    return {
      title: "FAQ Not Found",
      description: "The requested FAQ could not be found",
    }
  }

  return {
    title: faq.title,
    description: faq.excerpt,
  }
}

export async function generateStaticParams() {
  const slugs = await getAllFaqSlugs()
  return slugs.map((slug) => ({ slug }))
}

export default async function FaqPage({ params }: Props) {
  const { slug } = await params
  const faq = await getFaq(slug)

  if (!faq) {
    notFound()
  }

  const faqSchema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: [
      {
        "@type": "Question",
        name: faq.title,
        acceptedAnswer: {
          "@type": "Answer",
          text: faq.excerpt || faq.title,
        },
      },
    ],
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
      />
      <article className="max-w-4xl mx-auto">
        <header className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold mb-4">{faq.title}</h1>
          {faq.excerpt && <p className="text-xl text-gray-600 mb-6">{faq.excerpt}</p>}
        </header>

        <PortableTextRenderer value={faq.answer} className="prose max-w-none mb-12" />

        {faq.sources && faq.sources.length > 0 && (
          <section className="mb-12">
            <h2 className="text-xl font-bold mb-4">Sources</h2>
            <ul className="list-disc pl-5 space-y-2">
              {faq.sources.map((source, index) => (
                <li key={index} className="text-gray-700">
                  {source.title && source.url ? (
                    <a
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline"
                    >
                      {source.title}
                    </a>
                  ) : (
                    source.title || source.url
                  )}
                </li>
              ))}
            </ul>
          </section>
        )}

        {faq.relatedFaqs && faq.relatedFaqs.length > 0 && <RelatedFaqs faqs={faq.relatedFaqs} />}

        {faq.relatedContent && <RelatedContent content={faq.relatedContent} />}
      </article>
    </div>
  )
}
