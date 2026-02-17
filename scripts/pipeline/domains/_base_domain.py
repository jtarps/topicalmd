"""Abstract base for domain specialist configurations."""

from abc import ABC, abstractmethod
from typing import List


class BaseDomain(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Internal identifier, e.g. 'joint_pain'."""

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable name, e.g. 'Joint Pain Specialist'."""

    @property
    @abstractmethod
    def categories(self) -> List[str]:
        """Sanity content categories this domain covers."""

    @property
    @abstractmethod
    def content_types(self) -> List[str]:
        """Content types this domain can produce."""

    @abstractmethod
    def get_system_prompt_file(self) -> str:
        """Filename in prompts/ for the writer system prompt."""

    def matches_product(self, product: dict) -> bool:
        """Check if a product falls under this domain."""
        cat = product.get("category", "")
        use = product.get("use_case", "")
        return cat in self.categories or use in self.categories
