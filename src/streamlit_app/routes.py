import streamlit as st

def get_nav_items():
    """Return list of navigation items."""
    return {
        "Dashboard": "pages/home.py",
        "Upload VCF": "pages/upload_vcf.py",
        "Variant Explorer": "pages/variant_explorer.py",
        "Drug Response": "pages/drug_response.py",
        "Knowledge Graph": "pages/knowledge_graph.py",
        "Settings": "pages/settings.py"
    }

def navigate_to(page_name: str):
    """Programmatic navigation helper."""
    items = get_nav_items()
    if page_name in items:
        st.switch_page(items[page_name])
