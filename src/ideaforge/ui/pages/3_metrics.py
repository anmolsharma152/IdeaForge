"""Streamlit UI — Metrics & Analytics Dashboard."""

import asyncio
import pandas as pd
import plotly.express as px
import streamlit as st
from ideaforge.db.schema import ensure_schema
from ideaforge.memory.store import list_ideas, list_sessions

st.set_page_config(page_title="Metrics & Compounding Analytics — IdeaForge", page_icon="📊", layout="wide")

st.markdown("## 📊 MLOps & Compounding Memory Analytics")
st.markdown("Track workflow metrics, novelty score distributions, and memory compounding over time.")

ensure_schema()

async def _fetch_analytics():
    sessions = await list_sessions(limit=100)
    ideas = await list_ideas(limit=100)
    return sessions, ideas

try:
    sessions, ideas = asyncio.run(_fetch_analytics())
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Sessions", len(sessions))
    col2.metric("Total Vault Ideas", len(ideas))
    avg_novelty = 0.0
    if ideas:
        novelties = [i.scores.get("novelty", 0.5) for i in ideas if isinstance(i.scores, dict)]
        if novelties:
            avg_novelty = sum(novelties) / len(novelties)
    col3.metric("Avg Novelty Score", f"{avg_novelty:.2f}")

    st.markdown("---")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Workflow Distribution")
        if ideas:
            wf_counts = pd.DataFrame([{"Workflow": i.workflow} for i in ideas]).value_counts().reset_index()
            wf_counts.columns = ["Workflow", "Count"]
            fig_wf = px.pie(wf_counts, names="Workflow", values="Count", title="Ideas by Workflow Template", hole=0.4)
            st.plotly_chart(fig_wf, use_container_width=True)
        else:
            st.info("No data available yet.")
            
    with col_chart2:
        st.subheader("Rubric Scores Breakdown")
        if ideas:
            scores_list = []
            for idx, i in enumerate(ideas):
                if isinstance(i.scores, dict) and i.scores:
                    scores_list.append({
                        "Idea": i.title[:20],
                        "Novelty": i.scores.get("novelty", 0.5),
                        "Coherence": i.scores.get("coherence", 0.5),
                        "Usefulness": i.scores.get("usefulness", 0.5),
                    })
            if scores_list:
                df_scores = pd.DataFrame(scores_list)
                fig_scores = px.bar(df_scores, x="Idea", y=["Novelty", "Coherence", "Usefulness"], title="Evaluation Dimensions")
                st.plotly_chart(fig_scores, use_container_width=True)
            else:
                st.info("No score metadata available.")
        else:
            st.info("No data available yet.")

except Exception as e:
    st.error(f"Failed to compute analytics metrics: {e}")
