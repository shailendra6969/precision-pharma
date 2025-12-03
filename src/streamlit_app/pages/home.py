import streamlit as st
from src.streamlit_app.components.layout import page_container, render_header, render_footer
from src.streamlit_app.components.metrics import render_summary_metrics
from src.streamlit_app.utils.config import APP_TITLE

def render_home():
    """Render the Home Dashboard."""
    page_container("Dashboard")
    
    render_header(APP_TITLE, "Personalized Medicine Dashboard")
    
    st.markdown("""
    <div class="card">
        <h3>👋 Welcome Back, Dr. User</h3>
        <p>This platform combines genomics, machine learning, and knowledge graphs to provide 
        personalized medicine insights based on patient genetic variants.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Summary Metrics
    render_summary_metrics(genes_count=47, variants_count=1523, drugs_count=234)
    
    st.markdown("### 🚀 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container():
            st.markdown("#### 🧬 Upload VCF")
            st.write("Upload and parse new patient variant files.")
            if st.button("Go to Upload", key="btn_upload"):
                st.switch_page("pages/upload_vcf.py")
                
    with col2:
        with st.container():
            st.markdown("#### 💊 Predict Response")
            st.write("Run ADR risk and drug response models.")
            if st.button("Go to Predictions", key="btn_predict"):
                st.switch_page("pages/drug_response.py")
                
    with col3:
        with st.container():
            st.markdown("#### 📊 Knowledge Graph")
            st.write("Explore gene-drug interactions.")
            if st.button("Go to Explorer", key="btn_kg"):
                st.switch_page("pages/knowledge_graph.py")

    render_footer()

if __name__ == "__main__":
    render_home()
