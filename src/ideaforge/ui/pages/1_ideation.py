"""Streamlit UI — Ideation Studio."""

import asyncio
import streamlit as st
import ideaforge.workflows  # noqa: F401
from ideaforge.db.schema import ensure_schema
from ideaforge.graph.build import build_graph
from ideaforge.memory.store import create_session
from ideaforge.workflows.base import get_workflow, list_workflows

st.set_page_config(page_title="Ideation Studio — IdeaForge", page_icon="🎨", layout="wide")

st.markdown("## 🎨 Ideation Studio")
st.markdown("Run autonomous creative synthesis loops to turn vague goals into novel, actionable concepts.")

with st.sidebar:
    st.header("Ideation Settings")
    available_workflows = list_workflows()
    selected_wf_key = st.selectbox("Workflow Template", available_workflows, index=0)
    wf = get_workflow(selected_wf_key)
    
    if wf:
        st.caption(f"**{wf.name}**: {wf.description}")
        
    muses_count = st.slider("Muse Candidates per Round", min_value=2, max_value=10, value=5)
    max_rounds = st.slider("Max Iteration Rounds", min_value=1, max_value=5, value=3)

# Goal Input Form
with st.form("ideation_form"):
    goal_input = st.text_area(
        "Creative Goal or Prompt",
        placeholder="e.g. Novel non-obvious approaches to protein folding using cross-domain analogies",
        height=120,
    )
    submit_button = st.form_submit_button("🚀 Start Synthesis Loop", use_container_width=True)

if submit_button:
    if not goal_input.strip():
        st.error("Please enter a valid creative goal.")
    else:
        ensure_schema()
        graph = build_graph()
        initial_state = {
            "goal": goal_input.strip(),
            "workflow": selected_wf_key,
            "muse_count": muses_count,
            "max_iterations": max_rounds,
        }

        with st.status("Executing Dual-Process Graph...", expanded=True) as status:
            st.write("1️⃣ **Intake**: Normalizing prompt & searching web grounding...")
            
            async def _run_graph():
                state = await graph.ainvoke(initial_state)
                import uuid as _uuid
                idea_ids = [_uuid.UUID(i) for i in state.get("idea_ids", [])]
                await create_session(workflow=selected_wf_key, goal=goal_input, idea_ids=idea_ids)
                return state

            try:
                final_state = asyncio.run(_run_graph())
                status.update(label="Synthesis Complete! 🎉", state="complete", expanded=False)
            except Exception as e:
                status.update(label="Synthesis Failed", state="error", expanded=True)
                st.error(f"Error executing ideation workflow: {e}")
                final_state = None

        if final_state:
            # Display Refined Result
            refined = final_state.get("refined")
            if refined:
                st.success("### ═══ Synthesized Idea Card ═══")
                st.markdown(f"### **{refined.get('title', 'Untitled')}**")
                st.write(refined.get("body", ""))
                
                tags = refined.get("tags", [])
                if tags:
                    st.caption(f"**Tags:** {', '.join(tags)}")
                
                if final_state.get("idea_ids"):
                    st.info(f"**Stored in Vault (ID):** `{', '.join(final_state['idea_ids'])}`")
                if final_state.get("eval_notes"):
                    st.caption(f"**Eval Notes:** {final_state['eval_notes']}")

            # Candidates breakdown
            candidates = final_state.get("candidates", [])
            scores = final_state.get("scores", [])
            if candidates:
                st.markdown("---")
                st.markdown("### 💡 All Generated Candidates & Scores")
                
                cand_data = []
                for i, c in enumerate(candidates):
                    s = scores[i] if i < len(scores) else {}
                    cand_data.append({
                        "#": i + 1,
                        "Title": c.get("title", ""),
                        "Description": c.get("body", ""),
                        "Novelty": f"{s.get('novelty', 0):.2f}" if s else "-",
                        "Coherence": f"{s.get('coherence', 0):.2f}" if s else "-",
                        "Usefulness": f"{s.get('usefulness', 0):.2f}" if s else "-",
                        "Overall": f"{s.get('overall', 0):.2f}" if s else "-",
                    })
                
                st.dataframe(cand_data, use_container_width=True)
