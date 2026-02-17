"""Pre-built GROQ queries for gap detection and content inventory."""

# Products that have no review document pointing at them
PRODUCTS_WITHOUT_REVIEWS = """
*[_type == "product"]{
  _id, name, brand, category, activeIngredient
} | order(name asc)
[!(_id in *[_type == "review"].product._ref)]
"""

# Count of published content by document type
CONTENT_COUNTS_BY_TYPE = """
{
  "reviews": count(*[_type == "review"]),
  "useCases": count(*[_type == "useCase"]),
  "comparisons": count(*[_type == "comparison"]),
  "faqs": count(*[_type == "faq"]),
  "ingredients": count(*[_type == "ingredient"]),
  "products": count(*[_type == "product"])
}
"""

# Existing use-case slugs (to avoid duplicating best-for guides)
EXISTING_USECASE_SLUGS = """
*[_type == "useCase"].slug.current
"""

# Existing review slugs
EXISTING_REVIEW_SLUGS = """
*[_type == "review"].slug.current
"""

# Existing comparison slugs
EXISTING_COMPARISON_SLUGS = """
*[_type == "comparison"].slug.current
"""

# All products with their basic info (for research agent)
ALL_PRODUCTS = """
*[_type == "product"]{
  _id, name, brand, category, activeIngredient, mechanism
} | order(name asc)
"""

# Use-case categories currently covered
USECASE_CATEGORIES = """
*[_type == "useCase"].categories[]
"""

# Find a product by exact name (case-insensitive)
PRODUCT_BY_NAME = """
*[_type == "product" && lower(name) == lower($name)][0]{
  _id, name, brand
}
"""

# Find a product by partial name match (for fuzzy lookups)
PRODUCT_BY_NAME_CONTAINS = """
*[_type == "product" && lower(name) match lower($term)]{
  _id, name, brand
} | order(name asc)[0..4]
"""

# All existing reviews with their slugs and product names (for internal linking)
EXISTING_REVIEWS_WITH_PRODUCTS = """
*[_type == "review"]{
  "slug": slug.current,
  title,
  "productName": product->name
} | order(title asc)
"""
