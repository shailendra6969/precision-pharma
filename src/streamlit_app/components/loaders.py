import streamlit as st
from contextlib import contextmanager

@contextmanager
def custom_spinner(text: str = "Processing..."):
    """Custom styled spinner context manager."""
    with st.spinner(text):
        yield

def render_progress_bar(progress: float, text: str = None):
    """Render a progress bar."""
    st.progress(progress, text=text)
