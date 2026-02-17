"""Stage 1 — Research Agent: detects content gaps and builds a research brief."""

import json
import logging
from pathlib import Path
from typing import List

from scripts.pipeline.agents.base_agent import call_llm, load_prompt
from scripts.pipeline.config import AFFILIATE_PRODUCTS_PATH, RESEARCH_MODEL
from scripts.pipeline.models import ResearchBrief
from scripts.pipeline.publishing import sanity_client
from scripts.pipeline.publishing.sanity_queries import (
    CONTENT_COUNTS_BY_TYPE,
    EXISTING_COMPARISON_SLUGS,
    EXISTING_REVIEW_SLUGS,
    EXISTING_USECASE_SLUGS,
    PRODUCTS_WITHOUT_REVIEWS,
)

log = logging.getLogger(__name__)


def _load_affiliate_products() -> list:
    with open(AFFILIATE_PRODUCTS_PATH, "r") as f:
        data = json.load(f)
    return data.get("products", [])


def _gather_gaps(dry_run: bool = False) -> dict:
    """Query Sanity for content gaps. In dry_run mode, return empty placeholders."""
    if dry_run:
        return {
            "products_without_reviews": [],
            "content_counts": {"reviews": 0, "useCases": 0, "comparisons": 0, "faqs": 0},
            "existing_usecase_slugs": [],
            "existing_review_slugs": [],
            "existing_comparison_slugs": [],
        }

    try:
        return {
            "products_without_reviews": sanity_client.query(PRODUCTS_WITHOUT_REVIEWS),
            "content_counts": sanity_client.query(CONTENT_COUNTS_BY_TYPE),
            "existing_usecase_slugs": sanity_client.query(EXISTING_USECASE_SLUGS),
            "existing_review_slugs": sanity_client.query(EXISTING_REVIEW_SLUGS),
            "existing_comparison_slugs": sanity_client.query(EXISTING_COMPARISON_SLUGS),
        }
    except Exception as e:
        log.warning("Could not query Sanity for gaps: %s — using affiliate data only", e)
        return {
            "products_without_reviews": [],
            "content_counts": {},
            "existing_usecase_slugs": [],
            "existing_review_slugs": [],
            "existing_comparison_slugs": [],
        }


def run(
    domain_filter: str = "all",
    dry_run: bool = False,
) -> tuple:
    """Run the research agent.

    Returns (list[ResearchBrief], total_tokens_used).
    """
    products = _load_affiliate_products()
    gaps = _gather_gaps(dry_run=dry_run)

    product_summary = json.dumps(
        [
            {
                "product_name": p["product_name"],
                "brand": p["brand"],
                "category": p.get("category", ""),
                "use_case": p.get("use_case", ""),
                "mechanism": p.get("mechanism", ""),
                "asin": p.get("asin", ""),
            }
            for p in products
        ],
        indent=2,
    )

    user_prompt = f"""Here is the current content inventory and available product data.

## Content Gaps from CMS
Products without reviews: {json.dumps(gaps['products_without_reviews'][:20], indent=2)}
Content counts: {json.dumps(gaps['content_counts'], indent=2)}
Existing use-case slugs: {json.dumps(gaps['existing_usecase_slugs'][:30])}
Existing review slugs: {json.dumps(gaps['existing_review_slugs'][:30])}
Existing comparison slugs: {json.dumps(gaps['existing_comparison_slugs'][:30])}

## Available Products
{product_summary}

## Domain filter
Only suggest content for domain: {domain_filter}
(If "all", suggest across all domains.)

## Task
Analyze the gaps and suggest exactly 3 high-priority articles to create. For each article provide:
- topic: the article title
- content_type: one of "review", "best-for", "comparison", "faq"
- domain: one of "joint_pain", "muscle_pain", "product_review"
- target_product: product name if a review, otherwise null
- keywords: list of 3-5 SEO keywords
- gap_reason: why this content is needed (1 sentence)
- relevant_products: list of product_name strings (5-8) to include

Return a JSON object with a single key "briefs" containing the array of 3 objects."""

    system = load_prompt("research_system.txt")
    result = call_llm(system, user_prompt, json_mode=True, model=RESEARCH_MODEL)
    raw_briefs = result["content"].get("briefs", [])

    # Enrich each brief with full product data
    product_lookup = {p["product_name"]: p for p in products}
    briefs: List[ResearchBrief] = []
    for rb in raw_briefs:
        relevant = [
            product_lookup[name]
            for name in rb.get("relevant_products", [])
            if name in product_lookup
        ]
        briefs.append(
            ResearchBrief(
                topic=rb["topic"],
                content_type=rb["content_type"],
                domain=rb["domain"],
                target_product=rb.get("target_product"),
                keywords=rb.get("keywords", []),
                gap_reason=rb.get("gap_reason", ""),
                relevant_products=relevant,
            )
        )

    total_tokens = result["input_tokens"] + result["output_tokens"]
    log.info("Research agent produced %d briefs (%d tokens)", len(briefs), total_tokens)
    return briefs, total_tokens
