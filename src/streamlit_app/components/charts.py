import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List

def render_variant_distribution(df: pd.DataFrame):
    """Render variant consequence distribution chart."""
    if df.empty:
        st.info("No data to display")
        return

    if 'consequence' not in df.columns:
        st.warning("Missing 'consequence' column")
        return

    counts = df['consequence'].value_counts().reset_index()
    counts.columns = ['Consequence', 'Count']
    
    fig = px.pie(
        counts, 
        values='Count', 
        names='Consequence',
        title='Variant Consequences',
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Blues_r
    )
    fig.update_layout(margin=dict(t=40, b=0, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)

def render_adr_risk_gauge(probability: float):
    """Render a gauge chart for ADR risk."""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = probability * 100,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "ADR Risk Probability"},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "#2c5282"},
            'steps': [
                {'range': [0, 33], 'color': "#e6fffa"},
                {'range': [33, 66], 'color': "#ebf8ff"},
                {'range': [66, 100], 'color': "#fff5f5"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': probability * 100
            }
        }
    ))
    fig.update_layout(height=300, margin=dict(t=40, b=0, l=20, r=20))
    st.plotly_chart(fig, use_container_width=True)

def render_shap_waterfall(explanation: Dict):
    """
    Render a simplified waterfall chart from SHAP explanation data.
    Expected explanation format: {'base_value': float, 'values': dict}
    """
    # This is a mock implementation since we don't have raw SHAP objects in frontend
    # In a real app, we'd pass the SHAP object or a specialized dict
    st.info("SHAP visualization placeholder")
