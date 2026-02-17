"""Stage 3 — Writer Agent: dispatches to the correct domain specialist and produces full markdown."""

import json
import logging
from typing import Dict, List

from slugify import slugify

from scripts.pipeline.agents.base_agent import call_llm, load_prompt
from scripts.pipeline.config import WRITER_MODEL
from scripts.pipeline.models import Article, ArticleOutline, ResearchBrief
from scripts.pipeline.publishing import sanity_client
from scripts.pipeline.publishing.sanity_queries import EXISTING_REVIEWS_WITH_PRODUCTS

log = logging.getLogger(__name__)

# Map domain names to their prompt files
_DOMAIN_PROMPTS: Dict[str, str] = {
    "joint_pain": "writer_joint_pain_system.txt",
    "muscle_pain": "writer_muscle_pain_system.txt",
    "product_review": "writer_product_review_system.txt",
}


def _build_internal_links(products: list, existing_reviews: list) -> str:
    """Build a reference table of internal links for alternative products.

    Maps product names to their review page URL (if a review exists)
    or their product slug URL as fallback.
    """
    # Build lookup: product name -> review slug
    review_lookup = {}
    for r in existing_reviews:
        if r.get("productName") and r.get("slug"):
            review_lookup[r["productName"].lower()] = r["slug"]

    lines = []
    for p in products:
        name = p["product_name"]
        name_lower = name.lower()
        product_slug = slugify(name)

        if name_lower in review_lookup:
            url = f"/review/{review_lookup[name_lower]}"
            lines.append(f"- {name}: [{name}]({url}) (review page)")
        else:
            url = f"/review/{product_slug}"
            lines.append(f"- {name}: [{name}]({url}) (product page)")

    return "\n".join(lines)


def run(brief: ResearchBrief, outline: ArticleOutline, dry_run: bool = False) -> tuple:
    """Run the writer agent with the appropriate domain specialist.

    Returns (Article, total_tokens_used).
    """
    domain = brief["domain"]
    prompt_file = _DOMAIN_PROMPTS.get(domain, "writer_joint_pain_system.txt")
    system_prompt = load_prompt(prompt_file)

    product_details = json.dumps(
        [
            {
                "product_name": p["product_name"],
                "brand": p["brand"],
                "active_ingredient": p.get("active_ingredient", ""),
                "mechanism": p.get("mechanism", ""),
                "price_range": p.get("price_range", ""),
                "notes": p.get("notes", ""),
                "form": p.get("form", ""),
            }
            for p in brief["relevant_products"][:8]
        ],
        indent=2,
    )

    sections_json = json.dumps(
        [
            {
                "heading": s["heading"],
                "level": s["level"],
                "key_points": s["key_points"],
                "target_word_count": s["target_word_count"],
                "sources_to_cite": s["sources_to_cite"],
                "affiliate_placement": s["affiliate_placement"],
            }
            for s in outline["sections"]
        ],
        indent=2,
    )

    # Fetch existing reviews so the writer can link to alternatives
    existing_reviews: list = []
    if not dry_run:
        try:
            existing_reviews = sanity_client.query(EXISTING_REVIEWS_WITH_PRODUCTS)
        except Exception as e:
            log.warning("Could not fetch existing reviews for linking: %s", e)

    internal_links = _build_internal_links(brief["relevant_products"], existing_reviews)

    target_words = outline['total_target_words']

    user_prompt = f"""Write a COMPLETE {target_words}-word article based on this outline. You MUST write at least {target_words} words.

## Article Details
- Title: {outline['title']}
- Content Type: {outline['content_type']}
- MINIMUM Word Count: {target_words} words (this is a hard requirement — articles under {int(target_words * 0.85)} words will be rejected)
- SEO Keywords: {', '.join(brief['keywords'])}
- Featured Snippet Target: {outline.get('featured_snippet_target') or 'N/A'}

## Outline Sections
{sections_json}

## Product Data
{product_details}

## MANDATORY — Alternative Product Links
In the Alternatives section, you MUST list these specific products by name and link each one using the EXACT markdown links below. Do NOT write generic alternatives — use THESE products with THESE links:
{internal_links}

Example of what the Alternatives section should look like:
```
## Alternatives to Consider

- **[Aspercreme Original Pain Relief Cream](/review/aspercreme-original-pain-relief-cream-review)** — Uses trolamine salicylate, a non-NSAID option for those who want...
- **[Biofreeze Pain Relief Gel](/review/biofreeze-pain-relief-gel-review)** — Menthol-based cooling relief ideal for...
```

Each alternative should be a bullet point with the linked product name in bold, followed by a brief 1-sentence description of why someone might choose it over the reviewed product.

## Instructions
- Write in standard Markdown (## for h2, ### for h3, - for bullets, **bold**)
- Follow the outline section by section — do not skip any section
- Hit each section's target word count (±10%). The TOTAL article MUST reach {target_words} words minimum.
- Include E-E-A-T signals: cite real medical sources, demonstrate expertise
- Place product recommendations naturally with brief mentions of key ingredients
- Add a medical disclaimer at the end
- Do NOT fabricate clinical trial data or statistics

## FORMATTING — Scannable & Structured (IMPORTANT)
- Use **markdown tables** for data-heavy content like:
  - Key ingredients (| Ingredient | Concentration | Purpose |)
  - Product comparisons (| Feature | This Product | Competitor |)
  - Price/value breakdown (| Size | Price | Price per oz |)
- Use **bullet lists** for quick-reference items like pros/cons, who should use it, application tips
- Use **short paragraphs** (2-3 sentences max) for narrative sections like introduction and how-it-works
- Mix formats: a brief intro paragraph followed by a table or list is better than 4 paragraphs of the same info
- Readers scan before they read — make every section easy to skim with clear headers, bold key terms, and structured data

## CRITICAL — Completeness Rules (READ CAREFULLY)
1. You MUST write ALL sections from the outline. Count them and make sure every single one appears.
2. You MUST write a proper concluding section that summarizes key takeaways, restates who the product/treatment is best for, and encourages the reader to take action.
3. You MUST reach at least {target_words} words. If your draft feels short, expand each section with more detail, examples, and practical advice.
4. The article must feel COMPLETE and FINISHED — a reader should never feel like the article was cut short.
5. NEVER stop writing before finishing the conclusion and medical disclaimer.

Return ONLY the markdown article — no JSON wrapper, no code fences."""

    # Estimate max_tokens: ~1.3 tokens per word, with generous headroom
    estimated_tokens = int(target_words * 1.5) + 500
    result = call_llm(system_prompt, user_prompt, json_mode=False, max_tokens=max(estimated_tokens, 4096), model=WRITER_MODEL)
    markdown = result["content"]

    word_count = len(markdown.split())
    total_tokens = result["input_tokens"] + result["output_tokens"]

    article = Article(
        markdown=markdown,
        word_count=word_count,
        tokens_used=total_tokens,
    )

    log.info("Writer agent (%s): %d words, %d tokens", domain, word_count, total_tokens)
    return article, total_tokens
