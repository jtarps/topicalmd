import Link from "next/link"

type RelatedContentProps = {
  content: Array<{
    _id: string
    title: string
    slug: string
    _type: string
  }>
}

export default function RelatedContent({ content }: RelatedContentProps) {
  if (!content || content.length === 0) {
    return null
  }

  return (
    <section className="mt-12 pt-8 border-t">
      <h2 className="text-2xl font-bold mb-6">Related Content</h2>
      <div className="grid gap-4">
        {content.map((item) => (
          <Link
            key={item._id}
            href={getUrlForContentType(item._type, item.slug)}
            className="p-4 rounded-lg border hover:shadow-md transition-shadow"
          >
            <h3 className="font-medium hover:text-blue-600 transition-colors">{item.title}</h3>
          </Link>
        ))}
      </div>
    </section>
  )
}

function getUrlForContentType(type: string, slug: string): string {
  switch (type) {
    case "review":
      return `/review/${slug}`
    case "useCase":
      return `/best-for/${slug}`
    case "comparison":
      return `/compare/${slug}`
    case "ingredient":
      return `/ingredient/${slug}`
    case "faq":
      return `/faq/${slug}`
    default:
      return "/"
  }
}
