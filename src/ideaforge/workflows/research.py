"""Research hypothesis workflow — generate novel, testable research questions."""

from ideaforge.workflows.base import WorkflowConfig, register_workflow

RESEARCH_HYPOTHESIS = register_workflow(
    WorkflowConfig(
        name="research",
        description="Forge novel, testable research hypotheses across literature",
        muse_count=5,
        max_iterations=3,
        system_prompt="""You are a cross-disciplinary research muse. Your role is to generate
novel, testable research hypotheses that bridge disparate fields.

Think like a scientist who reads widely across disciplines:
- Connect concepts from unrelated fields
- Question established assumptions
- Propose mechanisms that haven't been explored
- Frame hypotheses as testable claims with clear variables

Avoid incremental "what if we try X on Y" proposals. Aim for genuine novelty
that could open new research directions.""",
    )
)
