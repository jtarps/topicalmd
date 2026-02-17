"""Muscle Pain domain specialist — Dr. Marcus Rivera, Sports Medicine Writer."""

from typing import List

from scripts.pipeline.domains._base_domain import BaseDomain


class MusclePainDomain(BaseDomain):
    @property
    def name(self) -> str:
        return "muscle_pain"

    @property
    def display_name(self) -> str:
        return "Dr. Marcus Rivera, Sports Medicine Writer"

    @property
    def categories(self) -> List[str]:
        return ["muscle-pain", "sports", "back-pain"]

    @property
    def content_types(self) -> List[str]:
        return ["review", "best-for", "comparison", "faq"]

    def get_system_prompt_file(self) -> str:
        return "writer_muscle_pain_system.txt"
