import streamlit as st
from typing import Union

def render_metric_card(label: str, value: Union[str, int, float], delta: str = None, help: str = None):
    """Render a styled metric card."""
    st.metric(label=label, value=value, delta=delta, help=help)

def render_summary_metrics(genes_count: int, variants_count: int, drugs_count: int):
    """Render the standard 3-column summary metrics."""
    col1, col2, col3 = st.columns(3)
    with col1:
        render_metric_card("Analyzed Genes", genes_count, "drug-metabolizers", "Total number of pharmacogenes analyzed")
    with col2:
        render_metric_card("Annotated Variants", f"{variants_count:,}", "clinvar/gnomad", "Total variants identified and annotated")
    with col3:
        render_metric_card("Drug Interactions", drugs_count, "known-interactions", "Number of drugs with potential genomic interactions")
