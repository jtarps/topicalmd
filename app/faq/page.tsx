import Link from "next/link"
import { getAllFaqs } from "@/lib/sanity"
import type { Metadata } from "next"

export const metadata: Metadata = {
  title: "Frequently Asked Questions - TopicalMD",
  description: "Answers to common questions about topical treatments, pain relief, and skin conditions.",
}

export default async function FaqPage() {
  const faqs = await getAllFaqs()

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="medical-breadcrumb">
        <Link href="/" className="medical-breadcrumb-item">
          Home
        </Link>
        <span className="medical-breadcrumb-separator">/</span>
        <span className="font-medium">FAQs</span>
      </div>

      <h1 className="text-3xl font-bold mb-6 text-primary">Frequently Asked Questions</h1>

      <div className="medical-info mb-8">
        <p>
          Find answers to common questions about topical treatments, their usage, effectiveness, and safety. All
          information is reviewed by healthcare professionals.
        </p>
      </div>

      {faqs.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <p className="text-xl text-gray-600">No FAQs found</p>
          <p className="mt-2 text-gray-500">Check back soon for answers to common questions</p>
        </div>
      ) : (
        <div className="space-y-4">
          {faqs.map((faq) => (
            <Link
              key={faq._id}
              href={`/faq/${faq.slug}`}
              className="medical-card p-4 block hover:bg-blue-50 transition-colors"
            >
              <h3 className="font-medium text-lg hover:text-primary transition-colors">{faq.title}</h3>
              {faq.excerpt && <p className="text-gray-600 mt-1">{faq.excerpt}</p>}
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
