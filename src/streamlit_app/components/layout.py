import streamlit as st
from pathlib import Path
from src.streamlit_app.utils.config import APP_TITLE, APP_ICON, COPYRIGHT

def load_css():
    """Load custom CSS."""
    theme_dir = Path(__file__).parent.parent / "theme"
    css_files = ["medical_theme.css", "dark_mode.css"]
    
    combined_css = ""
    for css_file in css_files:
        with open(theme_dir / css_file, "r") as f:
            combined_css += f.read() + "\n"
            
    st.markdown(f"<style>{combined_css}</style>", unsafe_allow_html=True)

def render_header(title: str, subtitle: str = None):
    """Render consistent page header."""
    st.title(title)
    if subtitle:
        st.markdown(f"*{subtitle}*")
    st.markdown("---")

def render_footer():
    """Render page footer."""
    st.markdown(
        f"""
        <div class="footer">
            {APP_TITLE} | {COPYRIGHT}
        </div>
        """,
        unsafe_allow_html=True
    )

def page_container(title: str, icon: str = APP_ICON, layout: str = "wide"):
    """Decorator or context manager for page setup."""
    st.set_page_config(
        page_title=f"{title} - {APP_TITLE}",
        page_icon=icon,
        layout=layout,
        initial_sidebar_state="expanded"
    )
    load_css()
    
    with st.sidebar:
        st.markdown(f"### {APP_ICON} Precision AI Engine")
        st.info("Environment: **Dev / Mock**")

