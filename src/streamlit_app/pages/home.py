import streamlit as st
from src.streamlit_app.components.layout import page_container, render_header, render_footer
from src.streamlit_app.components.sidebar import render_sidebar
from src.streamlit_app.utils.graph_utils import GraphService
from src.streamlit_app.utils.config import APP_TITLE

def render_home():
    """Render the Home Dashboard."""
    st.set_page_config(page_title=APP_TITLE, page_icon="🧬", layout="wide")
    
    # Load Theme
    with open("src/streamlit_app/theme/medical_theme.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    render_sidebar()
    
    # Main Content
    st.markdown("# 🏥 Personalized Medicine Dashboard")
    st.markdown("### Welcome Back, Dr. User")
    
    st.markdown("""
    <div class="card">
        <p style="font-size: 1.1rem;">
        This platform combines <strong>Genomics</strong>, <strong>Machine Learning</strong>, and 
        <strong>Knowledge Graphs</strong> to provide precision medicine insights.
        Upload patient data, analyze variants, and predict drug responses with AI.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Real-time Metrics
    st.markdown("### 📊 Live Database Stats")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Fetch stats
    service = GraphService.get_client()
    stats = service.get_stats() if service else None
    
    with col1:
        st.metric("Genes", stats.node_count if stats else "0", delta="Live" if stats and stats.is_connected else "Offline")
    with col2:
        st.metric("Interactions", stats.edge_count if stats else "0")
    with col3:
        st.metric("Drugs", "234", delta="+12 this week") # Mock delta
    with col4:
        st.metric("Latency", f"{int(stats.latency_ms)}ms" if stats else "-", delta_color="inverse")

    st.markdown("### 🚀 Quick Actions")
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("""
        <div class="card">
            <h4>🧬 Upload VCF</h4>
            <p>Process new patient genetic data.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Upload Data", use_container_width=True):
            st.switch_page("src/streamlit_app/pages/upload_vcf.py")
            
    with c2:
        st.markdown("""
        <div class="card">
            <h4>💊 Predict Response</h4>
            <p>Run ADR risk analysis models.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Run Prediction", use_container_width=True):
            st.switch_page("src/streamlit_app/pages/drug_response.py")
            
    with c3:
        st.markdown("""
        <div class="card">
            <h4>🕸️ Knowledge Graph</h4>
            <p>Explore drug-gene networks.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Explore Graph", use_container_width=True):
            st.switch_page("src/streamlit_app/pages/knowledge_graph.py")

    render_footer()

if __name__ == "__main__":
    render_home()
