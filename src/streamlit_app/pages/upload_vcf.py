import streamlit as st
from src.streamlit_app.components.layout import page_container, render_header, render_footer
from src.streamlit_app.components.loaders import custom_spinner
from src.streamlit_app.components.tables import render_dataframe
from src.streamlit_app.utils.variant_parser import VariantParserService
from src.streamlit_app.utils.data_loader import save_uploaded_file

def render_upload_vcf():
    """Render the VCF Upload page."""
    page_container("Upload VCF", icon="🧬")
    render_header("Upload Variants", "Parse and annotate patient VCF files")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 📁 File Upload")
        uploaded_file = st.file_uploader("Choose a VCF file", type=['vcf', 'vcf.gz'])

        if uploaded_file:
            tmp_path = save_uploaded_file(uploaded_file)
            
            if tmp_path:
                try:
                    with custom_spinner("Parsing and annotating variants..."):
                        df = VariantParserService.parse_vcf(tmp_path)
                        
                    st.success(f"Successfully parsed {len(df)} variants!")
                    
                    # Save to session state
                    st.session_state['variants_df'] = df
                    st.session_state['vcf_filename'] = uploaded_file.name
                    
                    render_dataframe(df.head(50))
                    
                except Exception as e:
                    st.error(f"Error parsing VCF: {e}")
                
    with col2:
        st.markdown("### ℹ️ Instructions")
        st.info("""
        1. Upload a standard `.vcf` or `.vcf.gz` file.
        2. The system will automatically:
            - Parse variants
            - Annotate with ClinVar & gnomAD
            - Calculate CADD scores
            - Identify drug-metabolizer genes
        3. Proceed to **Variant Explorer** or **Drug Response** pages.
        """)
        
        if 'variants_df' in st.session_state:
            st.markdown("### 📊 Summary")
            stats = VariantParserService.get_summary_stats(st.session_state['variants_df'])
            st.metric("Total Variants", stats.get("total_variants", 0))
            st.metric("Unique Genes", stats.get("unique_genes", 0))
            
            pathogenic = stats.get("pathogenic_count", 0)
            st.metric("Pathogenic Variants", pathogenic, delta="High Risk" if pathogenic > 0 else "Low Risk", delta_color="inverse")

    render_footer()

if __name__ == "__main__":
    render_upload_vcf()
