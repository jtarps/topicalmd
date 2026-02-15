import type { MetadataRoute } from "next"
import {
  getAllReviewSlugs,
  getAllUseCaseSlugs,
  getAllComparisonSlugs,
  getAllIngredientSlugs,
  getAllFaqSlugs,
} from "@/lib/sanity"

const BASE_URL = "https://topicalmd.com"

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const [reviewSlugs, useCaseSlugs, comparisonSlugs, ingredientSlugs, faqSlugs] =
    await Promise.all([
      getAllReviewSlugs(),
      getAllUseCaseSlugs(),
      getAllComparisonSlugs(),
      getAllIngredientSlugs(),
      getAllFaqSlugs(),
    ])

  const staticPages: MetadataRoute.Sitemap = [
    { url: BASE_URL, lastModified: new Date(), changeFrequency: "daily", priority: 1.0 },
    { url: `${BASE_URL}/reviews`, lastModified: new Date(), changeFrequency: "daily", priority: 0.9 },
    { url: `${BASE_URL}/best-for`, lastModified: new Date(), changeFrequency: "weekly", priority: 0.9 },
    { url: `${BASE_URL}/compare`, lastModified: new Date(), changeFrequency: "weekly", priority: 0.8 },
    { url: `${BASE_URL}/ingredient`, lastModified: new Date(), changeFrequency: "monthly", priority: 0.7 },
    { url: `${BASE_URL}/faq`, lastModified: new Date(), changeFrequency: "weekly", priority: 0.7 },
  ]

  const reviews = (reviewSlugs || []).map((slug: string) => ({
    url: `${BASE_URL}/review/${slug}`,
    lastModified: new Date(),
    changeFrequency: "weekly" as const,
    priority: 0.8,
  }))

  const useCases = (useCaseSlugs || []).map((slug: string) => ({
    url: `${BASE_URL}/best-for/${slug}`,
    lastModified: new Date(),
    changeFrequency: "weekly" as const,
    priority: 0.8,
  }))

  const comparisons = (comparisonSlugs || []).map((slug: string) => ({
    url: `${BASE_URL}/compare/${slug}`,
    lastModified: new Date(),
    changeFrequency: "weekly" as const,
    priority: 0.7,
  }))

  const ingredients = (ingredientSlugs || []).map((slug: string) => ({
    url: `${BASE_URL}/ingredient/${slug}`,
    lastModified: new Date(),
    changeFrequency: "monthly" as const,
    priority: 0.6,
  }))

  const faqs = (faqSlugs || []).map((slug: string) => ({
    url: `${BASE_URL}/faq/${slug}`,
    lastModified: new Date(),
    changeFrequency: "monthly" as const,
    priority: 0.5,
  }))

  return [...staticPages, ...reviews, ...useCases, ...comparisons, ...ingredients, ...faqs]
}
