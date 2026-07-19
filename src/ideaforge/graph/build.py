"""Build the LangGraph StateGraph for IdeaForge's dual-process loop.

Topology:
    intake → diverge → evaluate ──→ synthesize → persist → END
                           ↑        ╰──→ diverge (if not novel enough)
"""

from langgraph.graph import END, StateGraph

from ideaforge.graph.nodes.diverge import diverge_node
from ideaforge.graph.nodes.evaluate import evaluate_node
from ideaforge.graph.nodes.intake import intake_node
from ideaforge.graph.nodes.persist import persist_node
from ideaforge.graph.nodes.synthesize import synthesize_node
from ideaforge.models.state import AgentState


def route_after_evaluate(state: AgentState) -> str:
    return state.get("next_step", "stop")


def build_graph():
    workflow = StateGraph(AgentState)

    # Nodes
    workflow.add_node("intake", intake_node)
    workflow.add_node("diverge", diverge_node)
    workflow.add_node("evaluate", evaluate_node)
    workflow.add_node("synthesize", synthesize_node)
    workflow.add_node("persist", persist_node)

    # Entry
    workflow.set_entry_point("intake")

    # Linear flow: intake → diverge → evaluate
    workflow.add_edge("intake", "diverge")
    workflow.add_edge("diverge", "evaluate")

    # Conditional: evaluate → diverge | synthesize | stop
    workflow.add_conditional_edges(
        "evaluate",
        route_after_evaluate,
        {
            "diverge": "diverge",
            "synthesize": "synthesize",
            "stop": END,
        },
    )

    # synthesize → persist → END
    workflow.add_edge("synthesize", "persist")
    workflow.add_edge("persist", END)

    return workflow.compile()
