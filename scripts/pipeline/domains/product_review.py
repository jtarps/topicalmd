"""Product Review domain specialist — Alex Kim, Consumer Health Analyst."""

from typing import List

from scripts.pipeline.domains._base_domain import BaseDomain


class ProductReviewDomain(BaseDomain):
    @property
    def name(self) -> str:
        return "product_review"

    @property
    def display_name(self) -> str:
        return "Alex Kim, Consumer Health Analyst"

    @property
    def categories(self) -> List[str]:
        # Cross-domain — matches all product categories
        return [
            "arthritis", "joint-pain", "muscle-pain", "sports",
            "back-pain", "neuropathy", "nerve-pain", "general_pain",
            "capsaicin", "lidocaine", "cbd", "natural_arnica", "prescription",
        ]

    @property
    def content_types(self) -> List[str]:
        return ["review", "comparison"]

    def get_system_prompt_file(self) -> str:
        return "writer_product_review_system.txt"
