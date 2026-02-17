"""Builds Sanity mutations and pushes content — draft or published based on confidence score."""

import logging
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional

from slugify import slugify

from scripts.pipeline.config import PIPELINE_VERSION, PUBLISH_THRESHOLD
from scripts.pipeline.models import ArticleOutline, EditResult, ResearchBrief
from scripts.pipeline.publishing.content_formatter import to_portable_text
from scripts.pipeline.publishing.image_generator import acquire_image
from scripts.pipeline.publishing.sanity_client import mutate, query
from scripts.pipeline.publishing.sanity_queries import PRODUCT_BY_NAME, PRODUCT_BY_NAME_CONTAINS

log = logging.getLogger(__name__)


def _find_product_ref(product_name: str, dry_run: bool = False) -> Optional[dict]:
    """Look up a product in Sanity by name and return a reference dict.

    Tries exact match first, then falls back to partial name search.
    """
    if dry_run or not product_name:
        return None
    try:
        # Try exact match
        result = query(PRODUCT_BY_NAME, {"name": product_name})
        if result and result.get("_id"):
            log.info("Found product ref (exact) for '%s': %s", product_name, result["_id"])
            return {"_type": "reference", "_ref": result["_id"]}

        # Fuzzy fallback: search by brand + key word from product name
        # e.g. "Aspercreme Arthritis Pain Relief Gel" -> search "Aspercreme*"
        first_word = product_name.split()[0] if product_name else ""
        if first_word:
            results = query(PRODUCT_BY_NAME_CONTAINS, {"term": f"{first_word}*"})
            if results and len(results) > 0:
                best = results[0]
                log.info("Found product ref (fuzzy) for '%s': %s (%s)", product_name, best["_id"], best["name"])
                return {"_type": "reference", "_ref": best["_id"]}

    except Exception as e:
        log.warning("Could not look up product '%s': %s", product_name, e)
    return None


def _strip_markdown_links(text: str) -> str:
    """Convert markdown links [text](url) to just the text."""
    return re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)


def _extract_excerpt(markdown: str, max_len: int = 300) -> str:
    """Pull the first meaningful paragraph from markdown as the excerpt.

    Ensures the excerpt ends at a complete sentence, never mid-word or mid-sentence.
    """
    # Collect paragraph text (skip headings, tables, rules)
    paragraph = ""
    for line in markdown.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("|") or line.startswith("---"):
            if paragraph:
                break
            continue
        if line.startswith("-") or line.startswith("*") or re.match(r'^\d+\.', line):
            if paragraph:
                break
            continue
        paragraph += " " + line if paragraph else line

    if not paragraph:
        return ""

    # Strip markdown formatting and links
    clean = _strip_markdown_links(paragraph)
    clean = re.sub(r'[*_#>]', '', clean).strip()

    if len(clean) <= max_len:
        return clean

    # Truncate at the last complete sentence within max_len
    truncated = clean[:max_len]
    # Find the last sentence-ending punctuation
    last_period = max(truncated.rfind('. '), truncated.rfind('? '), truncated.rfind('! '))
    if last_period > 80:
        return truncated[:last_period + 1].strip()

    # If no sentence break found, at least end at a complete word
    last_space = truncated.rfind(' ')
    if last_space > 80:
        return truncated[:last_space].strip() + "..."

    return truncated.strip() + "..."


def _extract_pros_cons(markdown: str) -> tuple:
    """Pull pros/cons from review markdown as plain text (no markdown links)."""
    pros, cons = [], []
    current = None
    for line in markdown.splitlines():
        lower = line.strip().lower()
        if "pros" in lower and ("##" in line or "**" in lower):
            current = "pros"
            continue
        elif "cons" in lower and ("##" in line or "**" in lower):
            current = "cons"
            continue
        elif line.strip().startswith("#"):
            current = None
            continue

        item = re.sub(r'^[\s*\-]+', '', line).strip()
        if item:
            # Strip markdown link syntax — pros/cons are plain strings
            item = _strip_markdown_links(item)
            item = re.sub(r'[*_]', '', item).strip()
            if current == "pros":
                pros.append(item)
            elif current == "cons":
                cons.append(item)
    return pros[:8], cons[:8]


def _build_review_doc(brief: ResearchBrief, outline: ArticleOutline, edit: EditResult, image_ref: Optional[dict], dry_run: bool = False) -> dict:
    """Build a review document mutation."""
    doc_id = f"review-{outline['slug']}"
    if edit["confidence_score"] < PUBLISH_THRESHOLD:
        doc_id = f"drafts.{doc_id}"

    pros, cons = _extract_pros_cons(edit["final_markdown"])

    doc = {
        "_type": "review",
        "_id": doc_id,
        "title": outline["title"],
        "slug": {"_type": "slug", "current": outline["slug"]},
        "publishedAt": datetime.now(timezone.utc).isoformat(),
        "excerpt": _extract_excerpt(edit["final_markdown"]),
        "rating": 4.0,
        "generatedContent": edit["final_markdown"],
        "sourceModel": "gpt-4o",
        "content": to_portable_text(edit["final_markdown"]),
        "pros": pros,
        "cons": cons,
        "confidenceScore": edit["confidence_score"],
        "pipelineVersion": PIPELINE_VERSION,
    }
    if image_ref:
        doc["mainImage"] = image_ref

    # Attach product reference
    target_product = brief.get("target_product")
    if target_product:
        product_ref = _find_product_ref(target_product, dry_run=dry_run)
        if product_ref:
            doc["product"] = product_ref

    return doc


def _build_usecase_doc(brief: ResearchBrief, outline: ArticleOutline, edit: EditResult, image_ref: Optional[dict]) -> dict:
    """Build a useCase (best-for guide) document mutation."""
    doc_id = f"usecase-{outline['slug']}"
    if edit["confidence_score"] < PUBLISH_THRESHOLD:
        doc_id = f"drafts.{doc_id}"

    excerpt = _extract_excerpt(edit["final_markdown"])
    # Split intro from body: first paragraph is the intro
    lines = edit["final_markdown"].split("\n\n", 1)
    intro_md = lines[0] if lines else excerpt

    doc = {
        "_type": "useCase",
        "_id": doc_id,
        "title": outline["title"],
        "slug": {"_type": "slug", "current": outline["slug"]},
        "publishedAt": datetime.now(timezone.utc).isoformat(),
        "excerpt": excerpt,
        "metaTitle": outline["meta_title"],
        "metaDescription": outline["meta_description"],
        "author": "TopicalMD Editorial Team",
        "tags": brief.get("keywords", [])[:5],
        "categories": [],
        "introduction": to_portable_text(intro_md),
        "content": to_portable_text(edit["final_markdown"]),
        "confidenceScore": edit["confidence_score"],
        "pipelineVersion": PIPELINE_VERSION,
    }
    if image_ref:
        doc["mainImage"] = image_ref
    return doc


def _build_comparison_doc(brief: ResearchBrief, outline: ArticleOutline, edit: EditResult, image_ref: Optional[dict]) -> dict:
    """Build a comparison document mutation."""
    doc_id = f"comparison-{outline['slug']}"
    if edit["confidence_score"] < PUBLISH_THRESHOLD:
        doc_id = f"drafts.{doc_id}"

    excerpt = _extract_excerpt(edit["final_markdown"])
    lines = edit["final_markdown"].split("\n\n", 1)
    intro_md = lines[0] if lines else excerpt

    doc = {
        "_type": "comparison",
        "_id": doc_id,
        "title": outline["title"],
        "slug": {"_type": "slug", "current": outline["slug"]},
        "publishedAt": datetime.now(timezone.utc).isoformat(),
        "excerpt": excerpt,
        "introduction": to_portable_text(intro_md),
        "content": to_portable_text(edit["final_markdown"]),
        "confidenceScore": edit["confidence_score"],
        "pipelineVersion": PIPELINE_VERSION,
    }
    if image_ref:
        doc["mainImage"] = image_ref
    return doc


def _build_faq_doc(brief: ResearchBrief, outline: ArticleOutline, edit: EditResult, image_ref: Optional[dict]) -> dict:
    """Build an FAQ document mutation."""
    doc_id = f"faq-{outline['slug']}"
    if edit["confidence_score"] < PUBLISH_THRESHOLD:
        doc_id = f"drafts.{doc_id}"

    doc = {
        "_type": "faq",
        "_id": doc_id,
        "title": outline["title"],
        "slug": {"_type": "slug", "current": outline["slug"]},
        "publishedAt": datetime.now(timezone.utc).isoformat(),
        "excerpt": _extract_excerpt(edit["final_markdown"]),
        "answer": to_portable_text(edit["final_markdown"]),
        "confidenceScore": edit["confidence_score"],
        "pipelineVersion": PIPELINE_VERSION,
    }
    return doc


_BUILDERS = {
    "review": _build_review_doc,
    "best-for": _build_usecase_doc,
    "comparison": _build_comparison_doc,
    "faq": _build_faq_doc,
}


def publish_article(
    brief: ResearchBrief,
    outline: ArticleOutline,
    edit: EditResult,
    dry_run: bool = False,
) -> Dict:
    """Build the Sanity document mutation, acquire image, and push to Sanity.

    Returns a summary dict with id, type, score, decision, and any errors.
    """
    content_type = brief["content_type"]
    builder = _BUILDERS.get(content_type, _build_usecase_doc)

    # Acquire image: use product ASIN for reviews, DALL-E for editorial
    asin = None
    if brief.get("relevant_products"):
        asin = brief["relevant_products"][0].get("asin")

    image_ref = acquire_image(
        topic=brief["topic"],
        content_type=content_type,
        asin=asin,
        dry_run=dry_run,
    )

    # _build_review_doc accepts dry_run; others ignore it via **kwargs
    if content_type == "review":
        doc = builder(brief, outline, edit, image_ref, dry_run=dry_run)
    else:
        doc = builder(brief, outline, edit, image_ref)
    doc_id = doc["_id"]
    decision = "publish" if edit["confidence_score"] >= PUBLISH_THRESHOLD else "draft"

    mutations = [{"createOrReplace": doc}]

    if dry_run:
        log.info(
            "DRY RUN — would publish %s '%s' (score=%d, decision=%s)",
            content_type, outline["title"], edit["confidence_score"], decision,
        )
        return {
            "id": doc_id,
            "type": content_type,
            "title": outline["title"],
            "score": edit["confidence_score"],
            "decision": decision,
            "success": True,
            "has_image": image_ref is not None,
        }

    try:
        result = mutate(mutations, dry_run=False)
        log.info(
            "Published %s '%s' (score=%d, decision=%s)",
            content_type, outline["title"], edit["confidence_score"], decision,
        )
        return {
            "id": doc_id,
            "type": content_type,
            "title": outline["title"],
            "score": edit["confidence_score"],
            "decision": decision,
            "success": True,
            "has_image": image_ref is not None,
        }
    except Exception as e:
        log.error("Failed to publish '%s': %s", outline["title"], e)
        return {
            "id": doc_id,
            "type": content_type,
            "title": outline["title"],
            "score": edit["confidence_score"],
            "decision": decision,
            "success": False,
            "error": str(e),
        }
