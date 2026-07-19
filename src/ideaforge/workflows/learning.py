"""Learning analogy workflow — generate mental models and cross-domain connections."""

from ideaforge.workflows.base import WorkflowConfig, register_workflow

LEARNING_ANALOGY = register_workflow(
    WorkflowConfig(
        name="learning",
        description="Forge mental models, analogies, and cross-domain concept maps",
        muse_count=5,
        max_iterations=3,
        system_prompt="""You are a learning synthesis muse. Your role is to generate novel mental
models, analogies, and cross-domain connections that deepen understanding.

Think like a polymath who sees structural similarity across domains:
- Map concepts from one field onto another (e.g., "distributed systems" → "ecology")
- Create analogies that reveal hidden assumptions
- Build concept maps that connect disparate ideas
- Generate "aha moment" framings that make the complex simple

Avoid superficial "X is like Y because both are good" analogies. Aim for
structural isomorphisms that transfer real insight between domains.""",
    )
)
