"""Data contract for the Research Agent output."""

from typing import TypedDict, List, Optional


class ResearchBrief(TypedDict):
    topic: str                    # e.g. "Best Topical Creams for Arthritis in 2025"
    content_type: str             # review | best-for | comparison | faq
    domain: str                   # joint_pain | muscle_pain | product_review
    target_product: Optional[str] # product name (for reviews) or None
    keywords: List[str]           # SEO target keywords
    gap_reason: str               # why this content is needed
    relevant_products: List[dict] # subset of affiliate_products for the writer
