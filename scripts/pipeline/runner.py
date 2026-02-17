"""CLI orchestrator — runs the full multi-agent content pipeline.

Usage:
    python -m scripts.pipeline.runner --max-articles=3 --domain=all --dry-run
"""

import argparse
import logging
import sys
import time
from typing import List

from scripts.pipeline.agents import research_agent, outline_agent, writer_agent, format_validator, editor_agent
from scripts.pipeline.config import (
    EDITOR_MODEL, MAX_ARTICLES_PER_RUN, OUTLINE_MODEL, PUBLISH_THRESHOLD,
    RESEARCH_MODEL, WRITER_MODEL,
)
from scripts.pipeline.publishing.publisher import publish_article
from scripts.pipeline.utils.cost_tracker import CostTracker
from scripts.pipeline.utils.logging_config import setup_logging

log = logging.getLogger(__name__)


def run_pipeline(
    max_articles: int = MAX_ARTICLES_PER_RUN,
    domain: str = "all",
    dry_run: bool = False,
    verbose: bool = False,
) -> List[dict]:
    """Execute the full pipeline: Research → Outline → Write → Edit → Publish.

    Returns a list of result dicts (one per article).
    """
    setup_logging(verbose=verbose)
    tracker = CostTracker()
    results: List[dict] = []

    # ── Model configuration ──────────────────────────────────────────────
    log.info("=" * 60)
    log.info("MODEL CONFIGURATION")
    log.info("  Research: %s", RESEARCH_MODEL)
    log.info("  Outline:  %s", OUTLINE_MODEL)
    log.info("  Writer:   %s", WRITER_MODEL)
    log.info("  Editor:   %s", EDITOR_MODEL)
    log.info("=" * 60)

    # ── Stage 1: Research ───────────────────────────────────────────────
    log.info("")
    log.info("STAGE 1 — Research Agent (%s)", RESEARCH_MODEL)
    log.info("=" * 60)

    briefs, research_tokens = research_agent.run(domain_filter=domain, dry_run=dry_run)
    tracker.add_llm_usage(research_tokens // 2, research_tokens // 2)

    if not briefs:
        log.error("Research agent returned no briefs — aborting")
        return results

    briefs = briefs[:max_articles]
    log.info("Research agent suggested %d articles", len(briefs))

    for i, brief in enumerate(briefs):
        article_start = time.time()
        log.info("")
        log.info("-" * 60)
        log.info("ARTICLE %d/%d: %s", i + 1, len(briefs), brief["topic"])
        log.info("-" * 60)

        try:
            # ── Stage 2: Outline ────────────────────────────────────────
            log.info("  Stage 2 — Outline Agent")
            outline, outline_tokens = outline_agent.run(brief)
            tracker.add_llm_usage(outline_tokens // 2, outline_tokens // 2)

            # ── Stage 3: Writer ─────────────────────────────────────────
            log.info("  Stage 3 — Writer Agent (%s)", brief["domain"])
            article, writer_tokens = writer_agent.run(brief, outline, dry_run=dry_run)
            tracker.add_llm_usage(writer_tokens // 2, writer_tokens // 2)

            # ── Stage 3.5: Format Validation (no LLM) ─────────────────
            log.info("  Stage 3.5 — Format Validator")
            article, validation = format_validator.run(article, outline)
            if validation["issues"]:
                log.info("    %d issues found, %d auto-fixed", validation["issue_count"], len(validation["fixes_applied"]))

            # ── Stage 4: Editor ─────────────────────────────────────────
            log.info("  Stage 4 — Editor Agent")
            edit, editor_tokens = editor_agent.run(brief, outline, article, validation_issues=validation.get("issues", []))
            tracker.add_llm_usage(editor_tokens // 2, editor_tokens // 2)

            # ── Stage 5+6: Image + Publish ──────────────────────────────
            log.info("  Stage 5/6 — Image Acquisition + Publishing")
            pub_result = publish_article(brief, outline, edit, dry_run=dry_run)

            elapsed = time.time() - article_start
            pub_result["elapsed_seconds"] = round(elapsed, 1)
            results.append(pub_result)

            _log_article_result(pub_result, edit)

        except Exception as e:
            log.error("  FAILED: %s", e, exc_info=True)
            results.append({
                "title": brief["topic"],
                "type": brief["content_type"],
                "success": False,
                "error": str(e),
                "elapsed_seconds": round(time.time() - article_start, 1),
            })

    # ── Summary ─────────────────────────────────────────────────────────
    _log_summary(results, tracker, dry_run)
    return results


def _log_article_result(result: dict, edit) -> None:
    status = "PUBLISHED" if result.get("decision") == "publish" else "DRAFT"
    log.info(
        "  Result: %s | Score: %d | Image: %s | Time: %.1fs",
        status,
        result.get("score", 0),
        "yes" if result.get("has_image") else "no",
        result.get("elapsed_seconds", 0),
    )
    if edit.get("issues_found"):
        for issue in edit["issues_found"][:3]:
            log.info("    Issue: %s", issue)


def _log_summary(results: List[dict], tracker: CostTracker, dry_run: bool) -> None:
    log.info("")
    log.info("=" * 60)
    log.info("PIPELINE COMPLETE%s", " (DRY RUN)" if dry_run else "")
    log.info("=" * 60)

    success = sum(1 for r in results if r.get("success"))
    published = sum(1 for r in results if r.get("decision") == "publish")
    drafted = sum(1 for r in results if r.get("decision") == "draft")
    failed = len(results) - success

    log.info("  Articles: %d total | %d published | %d drafted | %d failed", len(results), published, drafted, failed)
    log.info("  %s", tracker.summary())

    # GitHub Actions step summary
    summary_lines = [
        "## Content Pipeline Run",
        f"- **Articles**: {len(results)} total, {published} published, {drafted} drafted, {failed} failed",
        f"- **Cost**: {tracker.summary()}",
        f"- **Dry run**: {dry_run}",
        "",
        "| Title | Type | Score | Decision |",
        "|-------|------|-------|----------|",
    ]
    for r in results:
        title = r.get("title", "Unknown")[:50]
        ctype = r.get("type", "?")
        score = r.get("score", "N/A")
        decision = r.get("decision", r.get("error", "error")[:20])
        summary_lines.append(f"| {title} | {ctype} | {score} | {decision} |")

    import os
    summary_file = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_file:
        with open(summary_file, "a") as f:
            f.write("\n".join(summary_lines) + "\n")


def main():
    parser = argparse.ArgumentParser(description="TopicalMD Multi-Agent Content Pipeline")
    parser.add_argument("--max-articles", type=int, default=MAX_ARTICLES_PER_RUN, help="Maximum articles to generate")
    parser.add_argument("--domain", type=str, default="all", choices=["all", "joint_pain", "muscle_pain", "product_review"], help="Domain filter")
    parser.add_argument("--dry-run", action="store_true", help="Run pipeline without pushing to Sanity")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    results = run_pipeline(
        max_articles=args.max_articles,
        domain=args.domain,
        dry_run=args.dry_run,
        verbose=args.verbose,
    )

    # Exit non-zero if all articles failed
    if results and all(not r.get("success") for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
