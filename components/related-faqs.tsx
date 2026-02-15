import Link from "next/link"

type RelatedFaqsProps = {
  faqs: Array<{
    _id: string
    title: string
    slug: string
  }>
}

export default function RelatedFaqs({ faqs }: RelatedFaqsProps) {
  if (!faqs || faqs.length === 0) {
    return null
  }

  return (
    <section className="mb-12">
      <h2 className="text-xl font-bold mb-4">Related Questions</h2>
      <div className="space-y-4">
        {faqs.map((faq) => (
          <Link
            key={faq._id}
            href={`/faq/${faq.slug}`}
            className="block p-4 rounded-lg border hover:shadow-md transition-shadow"
          >
            <h3 className="font-medium hover:text-blue-600 transition-colors">{faq.title}</h3>
          </Link>
        ))}
      </div>
    </section>
  )
}
