"""Stage 3.5 — Format Validator: lightweight structural checks between Writer and Editor.

No LLM calls — pure regex/string analysis. Catches mechanical issues that would
waste an expensive editor call, and auto-fixes what it can.
"""

import logging
import re
from typing import Dict, List, Tuple

from scripts.pipeline.models import Article, ArticleOutline

log = logging.getLogger(__name__)


def _normalize(text: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace for fuzzy matching."""
    return re.sub(r"[^a-z0-9 ]+", "", text.lower()).strip()


def _extract_headings(markdown: str) -> List[Dict[str, str]]:
    """Extract all headings from markdown with their level and text."""
    headings = []
    for match in re.finditer(r"^(#{1,4})\s+(.+)$", markdown, re.MULTILINE):
        headings.append({
            "level": len(match.group(1)),
            "text": match.group(2).strip().rstrip("#").strip(),
            "raw": match.group(0),
            "start": match.start(),
            "end": match.end(),
        })
    return headings


def _check_missing_sections(
    markdown: str, outline: ArticleOutline
) -> List[str]:
    """Check that every outline section appears as a heading in the article."""
    article_headings = [_normalize(h["text"]) for h in _extract_headings(markdown)]
    missing = []
    for section in outline["sections"]:
        expected = _normalize(section["heading"])
        # Fuzzy match: check if the key words appear in any heading
        key_words = [w for w in expected.split() if len(w) > 3]
        found = any(
            all(kw in ah for kw in key_words)
            for ah in article_headings
        ) if key_words else expected in " ".join(article_headings)
        if not found:
            missing.append(section["heading"])
    return missing


def _check_empty_headings(markdown: str) -> List[str]:
    """Find headings with no content before the next heading or end of file."""
    issues = []
    headings = _extract_headings(markdown)
    lines = markdown.split("\n")
    for i, h in enumerate(headings):
        # Find content between this heading and the next (or EOF)
        h_line = markdown[:h["start"]].count("\n")
        if i + 1 < len(headings):
            next_line = markdown[:headings[i + 1]["start"]].count("\n")
        else:
            next_line = len(lines)

        content_between = "\n".join(lines[h_line + 1:next_line]).strip()
        if not content_between:
            issues.append(f"Empty heading: '{h['text']}' has no content after it")
    return issues


def _check_tables(markdown: str) -> List[str]:
    """Validate markdown table formatting."""
    issues = []
    in_table = False
    expected_cols = 0
    table_start_line = 0

    for i, line in enumerate(markdown.split("\n"), 1):
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            cols = stripped.count("|") - 1
            if not in_table:
                in_table = True
                expected_cols = cols
                table_start_line = i
            elif cols != expected_cols:
                issues.append(
                    f"Table column mismatch at line {i}: expected {expected_cols} cols, got {cols} (table started at line {table_start_line})"
                )
        else:
            in_table = False
    return issues


def _check_links(markdown: str) -> List[str]:
    """Check for malformed markdown links."""
    issues = []
    # Find links missing closing paren or bracket
    for match in re.finditer(r"\[([^\]]*)\]\(([^)]*?)(?:\n|$)", markdown):
        issues.append(f"Possibly broken link: [{match.group(1)}]({match.group(2)}...")
    # Find bare URLs that should be linked
    for match in re.finditer(r"(?<!\()(https?://[^\s\)]+)(?!\))", markdown):
        url = match.group(1)
        # Skip if it's inside a markdown link already
        before = markdown[max(0, match.start() - 2):match.start()]
        if "(" not in before:
            issues.append(f"Bare URL should be a markdown link: {url[:60]}")
    return issues


def _check_word_count(article: Article, outline: ArticleOutline) -> List[str]:
    """Check if word count meets the target."""
    issues = []
    target = outline["total_target_words"]
    actual = article["word_count"]
    ratio = actual / target if target > 0 else 0

    if ratio < 0.70:
        issues.append(
            f"CRITICAL: Word count {actual} is only {ratio:.0%} of target {target} — article is severely short"
        )
    elif ratio < 0.85:
        issues.append(
            f"Word count {actual} is {ratio:.0%} of target {target} — article is under minimum"
        )
    return issues


def _check_abrupt_ending(markdown: str) -> List[str]:
    """Check if the article ends abruptly."""
    issues = []
    lines = [l.strip() for l in markdown.strip().split("\n") if l.strip()]
    if not lines:
        return ["Article is empty"]

    last_line = lines[-1]

    # Ends with a heading (no content after it)
    if re.match(r"^#{1,4}\s+", last_line):
        issues.append(f"Article ends with a heading and no content: '{last_line}'")

    # Ends mid-sentence (no terminal punctuation)
    if last_line and last_line[-1] not in ".!?*_)\"'":
        # Allow lines ending with markdown formatting
        if not last_line.endswith("---") and not last_line.endswith("|"):
            issues.append(f"Article may end mid-sentence: '...{last_line[-60:]}'")

    # Check for medical disclaimer (expected in all articles)
    lower_md = markdown.lower()
    if "disclaimer" not in lower_md and "medical advice" not in lower_md:
        issues.append("Missing medical disclaimer at end of article")

    return issues


def _auto_fix(markdown: str, issues: List[str]) -> Tuple[str, List[str]]:
    """Attempt to auto-fix mechanical issues. Returns (fixed_markdown, fixes_applied)."""
    fixed = markdown
    fixes = []

    # Fix 1: Remove trailing empty headings (## with nothing after)
    trailing_heading = re.search(r"\n(#{1,4}\s+[^\n]*)\s*$", fixed)
    if trailing_heading:
        heading_text = trailing_heading.group(1).strip()
        # Check if there's no content after this heading
        after = fixed[trailing_heading.end():].strip()
        if not after:
            fixed = fixed[:trailing_heading.start()].rstrip() + "\n"
            fixes.append(f"Removed trailing empty heading: '{heading_text}'")

    # Fix 2: Remove duplicate blank lines (3+ → 2)
    before = fixed
    fixed = re.sub(r"\n{3,}", "\n\n", fixed)
    if fixed != before:
        fixes.append("Collapsed excessive blank lines")

    # Fix 3: Fix heading spacing (ensure blank line before headings)
    before = fixed
    fixed = re.sub(r"([^\n])\n(#{1,4}\s+)", r"\1\n\n\2", fixed)
    if fixed != before:
        fixes.append("Added missing blank lines before headings")

    return fixed, fixes


def run(article: Article, outline: ArticleOutline) -> Tuple[Article, dict]:
    """Run format validation on the writer's output.

    Returns (possibly_fixed_article, validation_report).
    The report contains:
      - issues: list of issue strings
      - fixes_applied: list of auto-fix descriptions
      - missing_sections: list of outline sections not found
      - pass: bool — True if no critical issues remain after fixes
    """
    markdown = article["markdown"]
    all_issues: List[str] = []

    # Run all checks
    missing_sections = _check_missing_sections(markdown, outline)
    if missing_sections:
        for section in missing_sections:
            all_issues.append(f"Missing outline section: '{section}'")

    all_issues.extend(_check_empty_headings(markdown))
    all_issues.extend(_check_tables(markdown))
    all_issues.extend(_check_links(markdown))
    all_issues.extend(_check_word_count(article, outline))
    all_issues.extend(_check_abrupt_ending(markdown))

    # Auto-fix what we can
    fixed_markdown, fixes_applied = _auto_fix(markdown, all_issues)

    # Build fixed article if changes were made
    if fixes_applied:
        fixed_article = Article(
            markdown=fixed_markdown,
            word_count=len(fixed_markdown.split()),
            tokens_used=article["tokens_used"],
        )
    else:
        fixed_article = article

    # Determine pass/fail
    critical = any("CRITICAL" in issue for issue in all_issues)
    passed = not critical and len(all_issues) <= 3

    report = {
        "issues": all_issues,
        "fixes_applied": fixes_applied,
        "missing_sections": missing_sections,
        "pass": passed,
        "issue_count": len(all_issues),
    }

    if all_issues:
        log.info("Format validator: %d issues found, %d auto-fixed", len(all_issues), len(fixes_applied))
        for issue in all_issues[:5]:
            log.info("  - %s", issue)
    else:
        log.info("Format validator: all checks passed")

    return fixed_article, report
