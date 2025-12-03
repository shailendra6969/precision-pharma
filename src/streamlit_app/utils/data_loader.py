import streamlit as st
import pandas as pd
from typing import Optional, Any
from pathlib import Path

@st.cache_data
def load_csv(path: str) -> pd.DataFrame:
    """Load CSV data with caching."""
    try:
        return pd.read_csv(path)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

@st.cache_data
def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    """Convert DataFrame to CSV bytes for download."""
    return df.to_csv(index=False).encode('utf-8')

def save_uploaded_file(uploaded_file: Any, suffix: str = ".vcf") -> Optional[str]:
    """Save uploaded file to temp directory."""
    import tempfile
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.getbuffer())
            return tmp.name
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return None
