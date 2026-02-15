import Link from "next/link"
import Image from "next/image"
import { urlForImage } from "@/lib/sanity-image"

type FeaturedCardProps = {
  title: string
  description?: string
  image?: any
  slug: string
  variant?: "default" | "horizontal"
}

export default function FeaturedCard({ title, description, image, slug, variant = "default" }: FeaturedCardProps) {
  if (variant === "horizontal") {
    return (
      <Link href={slug} className="group block">
        <div className="medical-card flex items-start space-x-4 p-4 hover:bg-blue-50 transition-colors">
          {image && (
            <div className="relative h-16 w-16 flex-shrink-0">
              <Image
                src={urlForImage(image).width(200).height(200).url() || "/placeholder.svg"}
                alt={title}
                fill
                className="object-cover rounded-md"
                sizes="(max-width: 768px) 64px, 64px"
              />
            </div>
          )}
          <div>
            <h3 className="font-medium group-hover:text-primary transition-colors">{title}</h3>
            {description && <p className="text-sm text-gray-600 line-clamp-2">{description}</p>}
          </div>
        </div>
      </Link>
    )
  }

  return (
    <Link href={slug} className="group block">
      <div className="medical-card overflow-hidden">
        {image && (
          <div className="relative h-48 w-full">
            <Image
              src={urlForImage(image).width(400).height(300).url() || "/placeholder.svg"}
              alt={title}
              fill
              className="object-cover"
              sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
            />
          </div>
        )}
        <div className="p-4">
          <h3 className="font-medium group-hover:text-primary transition-colors">{title}</h3>
          {description && <p className="text-sm text-gray-600 mt-2 line-clamp-3">{description}</p>}
        </div>
      </div>
    </Link>
  )
}
