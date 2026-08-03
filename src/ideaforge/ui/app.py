"""Streamlit Web UI Entrypoint for IdeaForge — Creative Synthesis Engine."""

import streamlit as st

st.set_page_config(
    page_title="IdeaForge — Creative Synthesis Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Premium Modern Aesthetic Styling
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0b0f19 0%, #111827 50%, #0f172a 100%);
        color: #f8fafc;
    }
    
    /* Glassmorphism Card Effect */
    .glass-card {
        background: rgba(30, 41, 59, 0.6);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    
    .gradient-header {
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.5rem;
    }
    
    .metric-badge {
        display: inline-block;
        background: rgba(99, 102, 241, 0.2);
        color: #818cf8;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        border: 1px solid rgba(99, 102, 241, 0.4);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<h1 class="gradient-header">IdeaForge ⚡</h1>', unsafe_allow_html=True)
st.markdown("### Autonomous Creative Synthesis Engine with Compounding Memory")

st.markdown(
    """
    <div class="glass-card">
        <h4>Diverge → Evaluate → Synthesize → Persist</h4>
        <p>IdeaForge is a deliberate creativity engine. It breaks past bland LLM outputs by running structured dual-process ideation loops backed by pgvector persistent memory.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="glass-card">
            <h3>🎨 Ideation Studio</h3>
            <p>Run multi-round creative loops with real-time web search grounding and muse personas.</p>
            <span class="metric-badge">System 1 & System 2</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="glass-card">
            <h3>🧠 Idea Vault</h3>
            <p>Explore your vector-indexed memory graph, search similar concepts, and trace connections.</p>
            <span class="metric-badge">pgvector + Embeddings</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
        <div class="glass-card">
            <h3>📊 Metrics & Compounding</h3>
            <p>Analyze novelty decay, diversity scores, and ideation quality across runs.</p>
            <span class="metric-badge">MLOps & Analytics</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.info("👈 Select a tool from the sidebar navigation to get started!")
