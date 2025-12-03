import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
import tempfile
import os

def render_interactive_graph(nodes: list, edges: list, height="500px"):
    """
    Render an interactive network graph using PyVis.
    """
    try:
        net = Network(height=height, width="100%", bgcolor="#1E1E1E", font_color="white")
        
        # Add nodes
        for node in nodes:
            color = "#FF6B6B" if node.get("type") == "Gene" else "#4ECDC4" if node.get("type") == "Drug" else "#FFE66D"
            net.add_node(node["id"], label=node["label"], title=node.get("title"), color=color)
            
        # Add edges
        for edge in edges:
            net.add_edge(edge["source"], edge["target"], title=edge.get("type"))
            
        # Physics options
        net.force_atlas_2based()
        
        # Save to temp file and read back
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
            net.save_graph(tmp.name)
            with open(tmp.name, 'r', encoding='utf-8') as f:
                html_content = f.read()
            os.unlink(tmp.name)
            
        components.html(html_content, height=int(height.replace("px", "")) + 20)
        
    except Exception as e:
        st.error(f"Graph visualization failed: {e}")
