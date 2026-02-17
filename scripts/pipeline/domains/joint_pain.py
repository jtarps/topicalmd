"""Joint Pain domain specialist — Dr. Sarah Chen, Rheumatology Writer."""

from typing import List

from scripts.pipeline.domains._base_domain import BaseDomain


class JointPainDomain(BaseDomain):
    @property
    def name(self) -> str:
        return "joint_pain"

    @property
    def display_name(self) -> str:
        return "Dr. Sarah Chen, Rheumatology Writer"

    @property
    def categories(self) -> List[str]:
        return ["arthritis", "joint-pain", "knee-pain"]

    @property
    def content_types(self) -> List[str]:
        return ["review", "best-for", "comparison", "faq"]

    def get_system_prompt_file(self) -> str:
        return "writer_joint_pain_system.txt"
