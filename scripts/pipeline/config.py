"""Pipeline configuration — loads from environment with sensible defaults."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Walk up to find the .env closest to the project root
_project_root = Path(__file__).resolve().parent.parent.parent  # topical-treatments-new/
load_dotenv(_project_root / ".env")

# ── API Keys ────────────────────────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# ── Per-stage model assignments ─────────────────────────────────────────────
# Format: "provider/model" — provider is "openai", "anthropic", or "google"
# Override any stage via env vars (e.g. RESEARCH_MODEL=openai/gpt-4o)
RESEARCH_MODEL = os.getenv("RESEARCH_MODEL", "google/gemini-2.0-flash")
OUTLINE_MODEL = os.getenv("OUTLINE_MODEL", "google/gemini-2.0-flash")
WRITER_MODEL = os.getenv("WRITER_MODEL", "anthropic/claude-sonnet-4-5-20250929")
EDITOR_MODEL = os.getenv("EDITOR_MODEL", "anthropic/claude-sonnet-4-5-20250929")

# Legacy fallback (used if no provider-specific key is available)
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))

# ── Sanity ──────────────────────────────────────────────────────────────────
SANITY_PROJECT_ID = os.getenv("SANITY_PROJECT_ID", os.getenv("NEXT_PUBLIC_SANITY_PROJECT_ID", ""))
SANITY_DATASET = os.getenv("SANITY_DATASET", os.getenv("NEXT_PUBLIC_SANITY_DATASET", "production"))
SANITY_API_TOKEN = os.getenv("SANITY_API_TOKEN", "")
SANITY_API_VERSION = "2025-06-27"

# ── Pipeline thresholds ────────────────────────────────────────────────────
PUBLISH_THRESHOLD = int(os.getenv("PUBLISH_THRESHOLD", "80"))
MAX_ARTICLES_PER_RUN = int(os.getenv("MAX_ARTICLES_PER_RUN", "3"))

# ── Paths ───────────────────────────────────────────────────────────────────
PROJECT_ROOT = _project_root
SCRIPTS_DIR = _project_root / "scripts"
DATA_DIR = _project_root / "data"
AFFILIATE_PRODUCTS_PATH = DATA_DIR / "affiliate_products.json"
PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"

# ── Pipeline metadata ──────────────────────────────────────────────────────
PIPELINE_VERSION = "1.1.0"

# ── Active domains (add new domain module names here) ──────────────────────
ACTIVE_DOMAINS = ["joint_pain", "muscle_pain", "product_review"]

# ── Cost estimates (USD) ───────────────────────────────────────────────────
COST_PER_1K_INPUT_TOKENS = {
    "openai/gpt-4o": 0.0025,
    "anthropic/claude-sonnet-4-5-20250929": 0.003,
    "google/gemini-2.0-flash": 0.0001,
}
COST_PER_1K_OUTPUT_TOKENS = {
    "openai/gpt-4o": 0.01,
    "anthropic/claude-sonnet-4-5-20250929": 0.015,
    "google/gemini-2.0-flash": 0.0004,
}
COST_PER_DALLE_IMAGE = 0.04         # DALL-E 3 1024x1024

# ── Image settings ─────────────────────────────────────────────────────────
AMAZON_IMAGE_BASE = "https://m.media-amazon.com/images/I"
DALLE_IMAGE_SIZE = "1024x1024"
DALLE_IMAGE_QUALITY = "standard"
