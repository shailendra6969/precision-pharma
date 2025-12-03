import streamlit as st
import pandas as pd
from pathlib import Path
from src.streamlit_app.components.layout import page_container, render_header, render_footer
from src.streamlit_app.components.charts import render_variant_distribution
from src.streamlit_app.components.tables import render_dataframe
from src.streamlit_app.utils.data_loader import load_csv

def render_variant_explorer():
    """Render the Variant Explorer page."""
    page_container("Variant Explorer", icon="🔍")
    render_header("Variant Explorer", "Interactive analysis of annotated variants")

    # Load data
    df = None
    if 'variants_df' in st.session_state:
        df = st.session_state['variants_df']
    else:
        # Fallback to temp file
        csv_path = Path('/tmp/variants_annotated.csv')
        if csv_path.exists():
            df = load_csv(str(csv_path))

    if df is not None and not df.empty:
        # Sidebar Filters
        with st.sidebar:
            st.markdown("### Filters")
            
            if 'gene' in df.columns:
                all_genes = sorted(df['gene'].dropna().unique().tolist())
                selected_genes = st.multiselect("Select Genes", all_genes)
                if selected_genes:
                    df = df[df['gene'].isin(selected_genes)]
            
            if 'clinvar_significance' in df.columns:
                all_sigs = sorted(df['clinvar_significance'].dropna().unique().tolist())
                selected_sigs = st.multiselect("ClinVar Significance", all_sigs)
                if selected_sigs:
                    df = df[df['clinvar_significance'].isin(selected_sigs)]

        # Main Content
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📋 Variant Table")
            render_dataframe(df)
        
        with col2:
            st.markdown("### 📈 Distribution")
            render_variant_distribution(df)
            
        # Detailed View
        st.markdown("### 🔬 Variant Details")
        variant_ids = df['variant_id'].tolist() if 'variant_id' in df.columns else []
        selected_variant = st.selectbox("Select Variant to Inspect", variant_ids)
        
        if selected_variant:
            variant_data = df[df['variant_id'] == selected_variant].iloc[0]
            st.json(variant_data.to_dict())

    else:
        st.warning("⚠️ No variant data found. Please upload a VCF file first.")
        if st.button("Go to Upload"):
            st.switch_page("pages/upload_vcf.py")

    render_footer()

if __name__ == "__main__":
    render_variant_explorer()
