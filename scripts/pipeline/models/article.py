"""Data contract for the Writer Agent output."""

from typing import TypedDict


class Article(TypedDict):
    markdown: str          # full article in markdown
    word_count: int
    tokens_used: int       # total tokens consumed by the writer call
