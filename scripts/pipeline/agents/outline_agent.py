"""Stage 2 — Outline Agent: produces a section-by-section skeleton from a research brief."""

import json
import logging

from slugify import slugify

from scripts.pipeline.agents.base_agent import call_llm, load_prompt
from scripts.pipeline.config import OUTLINE_MODEL
from scripts.pipeline.models import ArticleOutline, OutlineSection, ResearchBrief

log = logging.getLogger(__name__)


def run(brief: ResearchBrief) -> tuple:
    """Run the outline agent.

    Returns (ArticleOutline, total_tokens_used).
    """
    product_names = [p["product_name"] for p in brief["relevant_products"][:8]]

    user_prompt = f"""Create a detailed article outline for the following topic.

## Article Info
- Topic: {brief['topic']}
- Content Type: {brief['content_type']}
- Domain: {brief['domain']}
- Target Product: {brief.get('target_product') or 'N/A (roundup article)'}
- SEO Keywords: {', '.join(brief['keywords'])}
- Products to include: {', '.join(product_names)}

## Task
Create a structured outline with:
1. title: SEO-friendly article title
2. slug: URL-friendly slug
3. meta_title: under 60 chars with primary keyword
4. meta_description: under 160 chars, compelling
5. content_type: "{brief['content_type']}"
6. sections: array of section objects, each with:
   - heading: section title
   - level: 2 for main sections, 3 for subsections
   - key_points: 3-5 bullet points of what to cover
   - target_word_count: integer
   - sources_to_cite: relevant sources (Mayo Clinic, NIH, ACR, etc.)
   - affiliate_placement: where to place product CTAs (or null)
7. total_target_words: sum of section word counts (aim for 1500-2500 words)
8. featured_snippet_target: a question this article could rank for in a featured snippet

Return JSON with these exact keys."""

    system = load_prompt("outline_system.txt")
    result = call_llm(system, user_prompt, json_mode=True, model=OUTLINE_MODEL)
    data = result["content"]

    sections = [
        OutlineSection(
            heading=s["heading"],
            level=s.get("level", 2),
            key_points=s.get("key_points", []),
            target_word_count=s.get("target_word_count", 200),
            sources_to_cite=s.get("sources_to_cite", []),
            affiliate_placement=s.get("affiliate_placement"),
        )
        for s in data.get("sections", [])
    ]

    outline = ArticleOutline(
        title=data.get("title", brief["topic"]),
        slug=data.get("slug", slugify(brief["topic"])),
        meta_title=data.get("meta_title", data.get("title", brief["topic"]))[:60],
        meta_description=data.get("meta_description", "")[:160],
        content_type=brief["content_type"],
        sections=sections,
        total_target_words=data.get("total_target_words", 2000),
        featured_snippet_target=data.get("featured_snippet_target"),
    )

    total_tokens = result["input_tokens"] + result["output_tokens"]
    log.info("Outline agent: '%s' — %d sections, %d target words", outline["title"], len(sections), outline["total_target_words"])
    return outline, total_tokens
