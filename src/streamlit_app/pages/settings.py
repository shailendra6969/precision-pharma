import streamlit as st
from src.streamlit_app.components.layout import page_container, render_header, render_footer
from src.streamlit_app.utils.config import VERSION

def render_settings():
    """Render the Settings page."""
    page_container("Settings", icon="⚙️")
    render_header("Settings", "Configure application preferences")

    st.markdown("### 🎨 Appearance")
    st.selectbox("Theme", ["Medical (Dark)", "Light Mode (Coming Soon)"])

    st.markdown("### 🔌 Integrations")
    st.text_input("ClinVar API Key", type="password")
    st.text_input("OpenAI API Key (for Explanations)", type="password")

    st.markdown("### 💾 Data Management")
    if st.button("Clear Cache"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.success("Cache cleared successfully!")

    st.markdown("### ℹ️ About")
    st.write(f"Precision Pharma AI Platform v{VERSION}")
    st.write("Built with Streamlit, FastAPI, and Neo4j.")

    render_footer()

if __name__ == "__main__":
    render_settings()
