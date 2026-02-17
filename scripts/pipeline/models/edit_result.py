"""Data contract for the Editor Agent output."""

from typing import TypedDict, List, Optional


class ScoreBreakdown(TypedDict):
    medical_accuracy: int      # 0-20
    structure_compliance: int   # 0-20
    eeat_signals: int          # 0-20
    readability: int           # 0-20
    seo_optimization: int      # 0-20


class EditResult(TypedDict):
    final_markdown: str
    confidence_score: int          # 0-100, sum of breakdown
    publish_decision: str          # "publish" | "draft"
    score_breakdown: ScoreBreakdown
    issues_found: List[str]
    corrections_made: List[str]
    tokens_used: int
