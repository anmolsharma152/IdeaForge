"""Streamlit UI — Idea Vault."""

import asyncio

import streamlit as st

from ideaforge.db.schema import ensure_schema
from ideaforge.memory.store import get_connections, list_ideas, search_similar

st.set_page_config(page_title="Idea Vault — IdeaForge", page_icon="🧠", layout="wide")

st.markdown("## 🧠 Idea Vault & Memory Graph")
st.markdown("Browse, search, and trace connection graphs across your persistent idea memory.")

ensure_schema()

tab_search, tab_browse = st.tabs(["🔍 Vector Similarity Search", "📚 Browse All Ideas"])

with tab_search:
    search_query = st.text_input("Semantic Search Query", placeholder="e.g. cross-domain analogies in biology")
    col_wf, col_limit = st.columns(2)
    with col_wf:
        search_wf = st.text_input("Filter Workflow (optional)", value="")
    with col_limit:
        top_k = st.slider("Top K Results", min_value=1, max_value=20, value=5)
        
    if search_query.strip():
        wf_arg = search_wf.strip() if search_wf.strip() else None
        
        async def _do_search():
            return await search_similar(query=search_query.strip(), limit=top_k, workflow=wf_arg)
            
        try:
            results = asyncio.run(_do_search())
            if not results:
                st.info("No matching ideas found.")
            else:
                st.markdown(f"Found **{len(results)}** similar ideas:")
                for r in results:
                    idea = r.idea
                    with st.expander(f"**{idea.title}** (Similarity: {r.similarity:.2f})"):
                        st.write(idea.body)
                        st.caption(f"Workflow: `{idea.workflow}` | ID: `{idea.id}` | Tags: `{', '.join(idea.tags)}`")
                        
                        # Load connections
                        async def _get_conns():
                            return await get_connections(idea.id)
                        conns = asyncio.run(_get_conns())
                        if conns:
                            st.markdown("**Connections:**")
                            for c in conns:
                                st.write(f"- `{c['relation']}` → **{c['linked_title']}** ({c['linked_workflow']})")
        except Exception as e:
            st.error(f"Search failed: {e}")

with tab_browse:
    async def _load_ideas():
        return await list_ideas(limit=50)
        
    try:
        ideas = asyncio.run(_load_ideas())
        if not ideas:
            st.info("No ideas stored in the database yet. Run an ideation session to populate the vault!")
        else:
            st.markdown(f"Total Stored Ideas: **{len(ideas)}**")
            for idea in ideas:
                with st.expander(f"**{idea.title}** ({idea.workflow})"):
                    st.write(idea.body)
                    st.caption(f"ID: `{idea.id}` | Tags: `{', '.join(idea.tags)}`")
                    if idea.scores:
                        st.json(idea.scores)
    except Exception as e:
        st.error(f"Failed to load ideas: {e}")
