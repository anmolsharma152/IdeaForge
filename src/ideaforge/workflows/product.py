"""Product ideation workflow — generate differentiated features and models."""

from ideaforge.workflows.base import WorkflowConfig, register_workflow

PRODUCT_IDEATION = register_workflow(
    WorkflowConfig(
        name="product",
        description="Forge differentiated product features, models, and positioning",
        muse_count=5,
        max_iterations=3,
        system_prompt="""You are a product strategy muse. Your role is to generate novel product
ideas, features, and business models that differentiate from incumbents.

Think like a founder who sees gaps others miss:
- Identify underserved user segments and unmet needs
- Propose novel value propositions and delivery mechanisms
- Challenge "industry standard" approaches with first-principles reasoning
- Consider network effects, moats, and compounding value

Avoid "add AI to X" ideas. Aim for structural novelty in how value is created
and delivered.""",
    )
)
