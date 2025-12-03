import streamlit as st
from src.streamlit_app.utils.config import VERSION
from src.streamlit_app.utils.health_check import SystemHealthCheck

def render_sidebar():
    """Render the unified application sidebar."""
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/dna-helix.png", width=64)
        st.title("Precision Pharma")
        st.caption(f"v{VERSION} | Clinical AI Platform")
        
        st.markdown("---")
        
        # Navigation
        st.markdown("### 🧭 Navigation")
        
        # We use st.page_link for smoother navigation in newer Streamlit versions
        # Fallback to standard markdown links or buttons if needed, but page_link is best.
        
        st.page_link("pages/home.py", label="Dashboard", icon="🏠")
        st.page_link("pages/upload_vcf.py", label="Upload VCF", icon="🧬")
        st.page_link("pages/variant_explorer.py", label="Variant Explorer", icon="🔍")
        st.page_link("pages/drug_response.py", label="Drug Response", icon="💊")
        st.page_link("pages/knowledge_graph.py", label="Knowledge Graph", icon="🕸️")
        st.page_link("pages/settings.py", label="Settings", icon="⚙️")
        
        st.markdown("---")
        
        # System Status Mini-Widget
        st.markdown("### 🟢 System Status")
        with st.spinner("Checking..."):
            # Lightweight check (just Neo4j)
            neo4j_status = SystemHealthCheck.check_neo4j()
            
        if neo4j_status["status"] == "online":
            st.markdown(f"**Neo4j**: <span class='status-online'>Online</span>", unsafe_allow_html=True)
            st.caption(f"Latency: {neo4j_status['latency']}")
        else:
            st.markdown(f"**Neo4j**: <span class='status-offline'>Offline</span>", unsafe_allow_html=True)
            if st.button("Reconnect"):
                st.cache_resource.clear()
                st.rerun()

        st.markdown("---")
        st.caption("© 2025 Precision Pharma AI")
