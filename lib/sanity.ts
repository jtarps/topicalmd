import { createClient } from "next-sanity"

const client = createClient({
  projectId: process.env.NEXT_PUBLIC_SANITY_PROJECT_ID || process.env.SANITY_PROJECT_ID,
  dataset: process.env.NEXT_PUBLIC_SANITY_DATASET || process.env.SANITY_DATASET || "production",
  apiVersion: "2023-05-03",
  useCdn: process.env.NODE_ENV === "production",
  token: process.env.SANITY_API_TOKEN,
})

// Homepage data
export async function getHomepageData() {
  try {
    return client.fetch(`{
      "featuredReviews": *[_type == "review"] | order(publishedAt desc) [0...3] {
        _id,
        title,
        "slug": slug.current,
        excerpt,
        mainImage
      },
      "featuredUseCases": *[_type == "useCase"] | order(publishedAt desc) [0...3] {
        _id,
        title,
        "slug": slug.current,
        excerpt,
        mainImage
      },
      "featuredComparisons": *[_type == "comparison"] | order(publishedAt desc) [0...3] {
        _id,
        title,
        "slug": slug.current,
        excerpt,
        mainImage
      },
      "featuredIngredients": *[_type == "ingredient"] | order(publishedAt desc) [0...2] {
        _id,
        title,
        "slug": slug.current,
        excerpt,
        mainImage
      },
      "featuredFaqs": *[_type == "faq"] | order(publishedAt desc) [0...2] {
        _id,
        title,
        "slug": slug.current,
        excerpt
      }
    }`)
  } catch (error) {
    console.error("Error fetching homepage data:", error)
    // Return empty data structure to prevent errors
    return {
      featuredReviews: [],
      featuredUseCases: [],
      featuredComparisons: [],
      featuredIngredients: [],
      featuredFaqs: [],
    }
  }
}

// Reviews
export async function getAllReviewSlugs() {
  try {
    const slugs = await client.fetch(`*[_type == "review"].slug.current`)
    return slugs
  } catch (error) {
    console.error("Error fetching review slugs:", error)
    return []
  }
}

export async function getReview(slug: string) {
  try {
    return client.fetch(
      `
      *[_type == "review" && slug.current == $slug][0] {
        _id,
        title,
        "slug": slug.current,
        excerpt,
        mainImage,
        rating,
        content,
        product->{
          name,
          image,
          price,
          affiliateLink,
          brand,
          size
        },
        pros,
        cons,
        "relatedContent": *[_type in ["review", "useCase", "comparison", "ingredient", "faq"] && references(^._id)] {
          _id,
          title,
          "slug": slug.current,
          _type
        }
      }
    `,
      { slug },
    )
  } catch (error) {
    console.error(`Error fetching review with slug ${slug}:`, error)
    return null
  }
}

// Use Cases
export async function getAllUseCaseSlugs() {
  try {
    const slugs = await client.fetch(`*[_type == "useCase"].slug.current`)
    return slugs
  } catch (error) {
    console.error("Error fetching useCase slugs:", error)
    return []
  }
}

export async function getUseCase(slug: string) {
  try {
    return client.fetch(
      `
      *[_type == "useCase" && slug.current == $slug][0] {
        _id,
        title,
        "slug": slug.current,
        excerpt,
        mainImage,
        introduction,
        content,
        categories,
        "recommendedProducts": *[_type == "product" && references(^._id)] {
          _id,
          name,
          image,
          price,
          rating,
          "slug": *[_type == "review" && references(^._id)][0].slug.current,
          excerpt
        },
        "relatedContent": *[_type in ["review", "useCase", "comparison", "ingredient", "faq"] && references(^._id)] {
          _id,
          title,
          "slug": slug.current,
          _type
        }
      }
    `,
      { slug },
    )
  } catch (error) {
    console.error(`Error fetching useCase with slug ${slug}:`, error)
    return null
  }
}

// Comparisons
export async function getAllComparisonSlugs() {
  try {
    const slugs = await client.fetch(`*[_type == "comparison"].slug.current`)
    return slugs
  } catch (error) {
    console.error("Error fetching comparison slugs:", error)
    return []
  }
}

export async function getComparison(slug: string) {
  try {
    return client.fetch(
      `
      *[_type == "comparison" && slug.current == $slug][0] {
        _id,
        title,
        "slug": slug.current,
        excerpt,
        mainImage,
        introduction,
        content,
        "products": products[]{
          "_id": product->_id,
          "name": product->name,
          "image": product->image,
          "price": product->price,
          "affiliateLink": product->affiliateLink,
          "brand": product->brand,
          "size": product->size,
          values
        },
        criteria,
        "winner": winner->{
          name,
          image
        },
        winnerReason,
        "relatedContent": *[_type in ["review", "useCase", "comparison", "ingredient", "faq"] && references(^._id)] {
          _id,
          title,
          "slug": slug.current,
          _type
        }
      }
    `,
      { slug },
    )
  } catch (error) {
    console.error(`Error fetching comparison with slug ${slug}:`, error)
    return null
  }
}

// Ingredients
export async function getAllIngredientSlugs() {
  try {
    const slugs = await client.fetch(`*[_type == "ingredient"].slug.current`)
    return slugs
  } catch (error) {
    console.error("Error fetching ingredient slugs:", error)
    return []
  }
}

export async function getIngredient(slug: string) {
  try {
    return client.fetch(
      `
      *[_type == "ingredient" && slug.current == $slug][0] {
        _id,
        title,
        "slug": slug.current,
        excerpt,
        mainImage,
        content,
        scientificName,
        origin,
        category,
        benefits,
        sideEffects,
        "relatedContent": *[_type in ["review", "useCase", "comparison", "ingredient", "faq"] && references(^._id)] {
          _id,
          title,
          "slug": slug.current,
          _type
        }
      }
    `,
      { slug },
    )
  } catch (error) {
    console.error(`Error fetching ingredient with slug ${slug}:`, error)
    return null
  }
}

// FAQs
export async function getAllFaqSlugs() {
  try {
    const slugs = await client.fetch(`*[_type == "faq"].slug.current`)
    return slugs
  } catch (error) {
    console.error("Error fetching FAQ slugs:", error)
    return []
  }
}

export async function getFaq(slug: string) {
  try {
    return client.fetch(
      `
      *[_type == "faq" && slug.current == $slug][0] {
        _id,
        title,
        "slug": slug.current,
        excerpt,
        answer,
        sources,
        "relatedFaqs": *[_type == "faq" && references(^._id)] {
          _id,
          title,
          "slug": slug.current
        },
        "relatedContent": *[_type in ["review", "useCase", "comparison", "ingredient"] && references(^._id)] {
          _id,
          title,
          "slug": slug.current,
          _type
        }
      }
    `,
      { slug },
    )
  } catch (error) {
    console.error(`Error fetching FAQ with slug ${slug}:`, error)
    return null
  }
}

// Condition category pages - find use cases by category slug
export async function getUseCasesByCategory(categorySlug: string) {
  try {
    return client.fetch(
      `
      {
        "useCases": *[_type == "useCase" && $categorySlug in categories] | order(publishedAt desc) {
          _id,
          title,
          "slug": slug.current,
          excerpt,
          mainImage,
          categories
        },
        "relatedProducts": *[_type == "product" && $categorySlug in useCases[]->categories] {
          _id,
          name,
          image,
          price,
          affiliateLink,
          brand,
          "slug": *[_type == "review" && references(^._id)][0].slug.current
        },
        "relatedReviews": *[_type == "review" && $categorySlug in product->useCases[]->categories] | order(publishedAt desc) [0...6] {
          _id,
          title,
          "slug": slug.current,
          excerpt,
          mainImage,
          rating
        }
      }
    `,
      { categorySlug },
    )
  } catch (error) {
    console.error(`Error fetching use cases for category ${categorySlug}:`, error)
    return { useCases: [], relatedProducts: [], relatedReviews: [] }
  }
}

// Get all products for comparison tool
export async function getAllProducts() {
  try {
    return client.fetch(`
      *[_type == "product"] | order(name asc) {
        _id,
        name,
        image,
        brand,
        price,
        size,
        form,
        activeIngredient,
        affiliateLink,
        OTC,
        "ingredients": ingredients[]->{ _id, title, "slug": slug.current }
      }
    `)
  } catch (error) {
    console.error("Error fetching all products:", error)
    return []
  }
}

// Get all content for reviews page
export async function getAllReviews() {
  try {
    return client.fetch(`
      *[_type == "review"] | order(publishedAt desc) {
        _id,
        title,
        "slug": slug.current,
        excerpt,
        mainImage,
        rating,
        product->{
          brand
        }
      }
    `)
  } catch (error) {
    console.error("Error fetching all reviews:", error)
    return []
  }
}

// Get all content for best-for page
export async function getAllUseCases() {
  try {
    return client.fetch(`
      *[_type == "useCase"] | order(publishedAt desc) {
        _id,
        title,
        "slug": slug.current,
        excerpt,
        mainImage,
        categories
      }
    `)
  } catch (error) {
    console.error("Error fetching all use cases:", error)
    return []
  }
}

// Get all content for comparisons page
export async function getAllComparisons() {
  try {
    return client.fetch(`
      *[_type == "comparison"] | order(publishedAt desc) {
        _id,
        title,
        "slug": slug.current,
        excerpt,
        mainImage
      }
    `)
  } catch (error) {
    console.error("Error fetching all comparisons:", error)
    return []
  }
}

// Get all content for ingredients page
export async function getAllIngredients() {
  try {
    return client.fetch(`
      *[_type == "ingredient"] | order(title asc) {
        _id,
        title,
        "slug": slug.current,
        excerpt,
        mainImage,
        category
      }
    `)
  } catch (error) {
    console.error("Error fetching all ingredients:", error)
    return []
  }
}

// Get all content for FAQs page
export async function getAllFaqs() {
  try {
    return client.fetch(`
      *[_type == "faq"] | order(publishedAt desc) {
        _id,
        title,
        "slug": slug.current,
        excerpt
      }
    `)
  } catch (error) {
    console.error("Error fetching all FAQs:", error)
    return []
  }
}
