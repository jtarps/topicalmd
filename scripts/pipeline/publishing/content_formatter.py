"""Thin wrapper around the existing markdown_to_portable_text converter."""

import sys
from pathlib import Path

# Add scripts/ to path so the legacy module is importable
_scripts_dir = Path(__file__).resolve().parent.parent.parent  # scripts/
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

from markdown_to_portable_text import markdown_to_portable_text  # noqa: E402


def to_portable_text(markdown: str) -> list:
    """Convert markdown string to Sanity Portable Text blocks."""
    return markdown_to_portable_text(markdown)
