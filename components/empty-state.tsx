import Link from "next/link"
import { FileQuestion } from "lucide-react"

type EmptyStateProps = {
  title: string
  message: string
  link?: {
    href: string
    label: string
  }
}

export default function EmptyState({ title, message, link }: EmptyStateProps) {
  return (
    <div className="text-center py-12 bg-gray-50 rounded-lg border border-gray-200">
      <div className="flex justify-center mb-4">
        <div className="bg-blue-100 p-3 rounded-full">
          <FileQuestion className="h-8 w-8 text-primary" />
        </div>
      </div>
      <h2 className="text-xl font-semibold text-gray-800 mb-2">{title}</h2>
      <p className="text-gray-600 mb-6 max-w-md mx-auto">{message}</p>
      {link && (
        <Link
          href={link.href}
          className="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary hover:bg-primary/90"
        >
          {link.label}
        </Link>
      )}
    </div>
  )
}
