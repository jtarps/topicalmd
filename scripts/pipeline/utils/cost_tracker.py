"""Simple token and cost tracker for pipeline runs."""

import logging

from scripts.pipeline.config import (
    COST_PER_1K_INPUT_TOKENS,
    COST_PER_1K_OUTPUT_TOKENS,
    COST_PER_DALLE_IMAGE,
)

log = logging.getLogger(__name__)


class CostTracker:
    def __init__(self):
        self.input_tokens = 0
        self.output_tokens = 0
        self.images_generated = 0
        self.images_fetched = 0

    def add_llm_usage(self, input_tokens: int, output_tokens: int) -> None:
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens

    def add_image(self, generated: bool = True) -> None:
        if generated:
            self.images_generated += 1
        else:
            self.images_fetched += 1

    @property
    def total_cost(self) -> float:
        # Use average cost across configured models (close enough for estimates)
        avg_input = sum(COST_PER_1K_INPUT_TOKENS.values()) / max(len(COST_PER_1K_INPUT_TOKENS), 1) if isinstance(COST_PER_1K_INPUT_TOKENS, dict) else COST_PER_1K_INPUT_TOKENS
        avg_output = sum(COST_PER_1K_OUTPUT_TOKENS.values()) / max(len(COST_PER_1K_OUTPUT_TOKENS), 1) if isinstance(COST_PER_1K_OUTPUT_TOKENS, dict) else COST_PER_1K_OUTPUT_TOKENS
        return (
            (self.input_tokens / 1000) * avg_input
            + (self.output_tokens / 1000) * avg_output
            + self.images_generated * COST_PER_DALLE_IMAGE
        )

    def summary(self) -> str:
        return (
            f"Tokens: {self.input_tokens:,} in / {self.output_tokens:,} out | "
            f"Images: {self.images_generated} generated, {self.images_fetched} fetched | "
            f"Est. cost: ${self.total_cost:.4f}"
        )
