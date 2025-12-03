import streamlit as st
import pandas as pd

def render_dataframe(df: pd.DataFrame, height: int = 400, use_container_width: bool = True):
    """Render a styled dataframe."""
    if df.empty:
        st.info("No data available to display.")
        return

    st.dataframe(
        df,
        height=height,
        use_container_width=use_container_width
    )

def render_aggrid(df: pd.DataFrame):
    """Placeholder for AgGrid implementation (if needed later)."""
    # For now, standard dataframe is sufficient but this abstraction allows easy upgrade
    render_dataframe(df)
