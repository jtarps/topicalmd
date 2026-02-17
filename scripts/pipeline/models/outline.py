"""Data contract for the Outline Agent output."""

from typing import TypedDict, List, Optional


class OutlineSection(TypedDict):
    heading: str
    level: int                      # 2 = h2, 3 = h3
    key_points: List[str]
    target_word_count: int
    sources_to_cite: List[str]      # URLs or publication names
    affiliate_placement: Optional[str]  # e.g. "product CTA after paragraph 2"


class ArticleOutline(TypedDict):
    title: str
    slug: str
    meta_title: str
    meta_description: str
    content_type: str               # review | best-for | comparison | faq
    sections: List[OutlineSection]
    total_target_words: int
    featured_snippet_target: Optional[str]  # the question to answer in a snippet
