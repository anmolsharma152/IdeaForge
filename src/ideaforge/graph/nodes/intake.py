"""Intake node — normalize prompt, load context."""

from ideaforge.models.state import AgentState


async def intake_node(state: AgentState) -> dict:
    goal = state["goal"]
    workflow = state.get("workflow", "general")

    context = f"Workflow: {workflow}\nGoal: {goal}"

    return {
        "context": context,
        "workflow": workflow,
        "iteration": 0,
        "max_iterations": state.get("max_iterations", 3),
        "candidates": [],
        "scores": [],
        "best_indices": [],
        "next_step": "diverge",
    }
