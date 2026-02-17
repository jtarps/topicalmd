"""Stage 4 — Editor Agent: scores article quality and polishes text."""

import json
import logging

from scripts.pipeline.agents.base_agent import call_llm, load_prompt
from scripts.pipeline.config import EDITOR_MODEL, PUBLISH_THRESHOLD
from scripts.pipeline.models import Article, ArticleOutline, EditResult, ResearchBrief

log = logging.getLogger(__name__)


def run(brief: ResearchBrief, outline: ArticleOutline, article: Article, validation_issues: list = None) -> tuple:
    """Run the editor agent.

    Returns (EditResult, total_tokens_used).
    """
    sections_list = [s["heading"] for s in outline["sections"]]

    validation_section = ""
    if validation_issues:
        issues_str = "\n".join(f"- {issue}" for issue in validation_issues)
        validation_section = f"""
## Pre-Editor Validation Issues (already detected)
The format validator flagged these issues before your review. Factor these into your scoring and fix them if possible:
{issues_str}
"""

    user_prompt = f"""Review and score the following article.

## Expected Outline Sections
{json.dumps(sections_list)}

## Article Metadata
- Title: {outline['title']}
- Content Type: {outline['content_type']}
- Target Words: {outline['total_target_words']}
- Actual Words: {article['word_count']}
- SEO Keywords: {', '.join(brief['keywords'])}
{validation_section}

## Article Content
{article['markdown']}

## Task
1. Score the article on 5 axes (each 0-20, total 0-100):
   - medical_accuracy: No fabricated claims, correct mechanisms, cites real sources
   - structure_compliance: All outline sections present, proper heading hierarchy
   - eeat_signals: Demonstrates expertise, cites authoritative sources, first-hand knowledge signals
   - readability: Scannable, clear language, good formatting, short paragraphs
   - seo_optimization: Keywords used naturally, featured snippet targeting, meta-friendly structure

2. List specific issues found (array of strings)

3. If the total score is below {PUBLISH_THRESHOLD} and issues are fixable:
   - Make corrections directly in the markdown
   - List corrections made

4. Return the (possibly corrected) article

Return JSON with keys:
- final_markdown: string (the full article, corrected if needed)
- confidence_score: integer 0-100
- publish_decision: "publish" if score >= {PUBLISH_THRESHOLD}, else "draft"
- score_breakdown: object with the 5 axes
- issues_found: array of strings
- corrections_made: array of strings (empty if no corrections)"""

    system = load_prompt("editor_system.txt")
    # Editor returns the full article inside JSON — needs enough tokens for article + scores + corrections
    editor_max_tokens = max(article["word_count"] * 3, 12000)
    result = call_llm(system, user_prompt, json_mode=True, model=EDITOR_MODEL, max_tokens=editor_max_tokens)
    data = result["content"]

    breakdown = data.get("score_breakdown", {})
    score = data.get("confidence_score", 0)

    # Sanity check: recalculate score from breakdown
    calc_score = sum(breakdown.get(k, 0) for k in [
        "medical_accuracy", "structure_compliance", "eeat_signals",
        "readability", "seo_optimization",
    ])
    if calc_score != score:
        log.warning("Score mismatch: stated=%d, calculated=%d — using calculated", score, calc_score)
        score = calc_score

    total_tokens = result["input_tokens"] + result["output_tokens"]

    edit = EditResult(
        final_markdown=data.get("final_markdown", article["markdown"]),
        confidence_score=score,
        publish_decision="publish" if score >= PUBLISH_THRESHOLD else "draft",
        score_breakdown=breakdown,
        issues_found=data.get("issues_found", []),
        corrections_made=data.get("corrections_made", []),
        tokens_used=total_tokens,
    )

    log.info(
        "Editor agent: score=%d (%s) — %d issues, %d corrections",
        score, edit["publish_decision"], len(edit["issues_found"]), len(edit["corrections_made"]),
    )
    return edit, total_tokens
