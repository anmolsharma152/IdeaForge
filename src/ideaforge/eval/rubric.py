"""Eval rubric — configurable scoring for idea quality."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RubricDimension:
    name: str
    weight: float
    description: str


@dataclass
class Rubric:
    name: str
    dimensions: list[RubricDimension] = field(default_factory=list)

    def compute_overall(self, scores: dict[str, float]) -> float:
        if not self.dimensions:
            return 0.0
        total = 0.0
        weight_sum = 0.0
        for dim in self.dimensions:
            if dim.name in scores:
                total += dim.weight * scores[dim.name]
                weight_sum += dim.weight
        return round(total / weight_sum, 4) if weight_sum > 0 else 0.0


DEFAULT_RUBRIC = Rubric(
    name="default",
    dimensions=[
        RubricDimension(name="novelty", weight=0.35, description="How non-obvious and fresh"),
        RubricDimension(
            name="coherence", weight=0.30, description="Logically sound and well-formed"
        ),
        RubricDimension(name="usefulness", weight=0.35, description="Actionable and valuable"),
    ],
)

RESEARCH_RUBRIC = Rubric(
    name="research",
    dimensions=[
        RubricDimension(name="novelty", weight=0.40, description="Genuinely new hypothesis"),
        RubricDimension(name="coherence", weight=0.25, description="Testable and logically sound"),
        RubricDimension(name="usefulness", weight=0.35, description="Could lead to experiments"),
    ],
)

RUBRICS: dict[str, Rubric] = {
    "default": DEFAULT_RUBRIC,
    "research": RESEARCH_RUBRIC,
}


def get_rubric(name: str = "default") -> Rubric:
    return RUBRICS.get(name, DEFAULT_RUBRIC)
