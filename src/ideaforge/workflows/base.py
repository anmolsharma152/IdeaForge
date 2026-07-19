"""Base workflow configuration — templates for different creative modes."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class WorkflowConfig:
    name: str
    description: str
    system_prompt: str
    muse_count: int = 5
    max_iterations: int = 3
    rubric: dict[str, float] = field(
        default_factory=lambda: {"novelty": 0.35, "coherence": 0.30, "usefulness": 0.35}
    )
    min_overall_score: float = 0.65


WORKFLOWS: dict[str, WorkflowConfig] = {}


def register_workflow(config: WorkflowConfig):
    WORKFLOWS[config.name] = config
    return config


def get_workflow(name: str) -> WorkflowConfig | None:
    return WORKFLOWS.get(name)


def list_workflows() -> list[str]:
    return list(WORKFLOWS.keys())
