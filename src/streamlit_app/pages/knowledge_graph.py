import streamlit as st
from src.streamlit_app.components.layout import page_container, render_header, render_footer
from src.streamlit_app.utils.graph_utils import GraphService

def render_knowledge_graph():
    """Render the Knowledge Graph page."""
    page_container("Knowledge Graph", icon="📊")
    render_header("Knowledge Graph Explorer", "Navigate gene-drug-variant relationships")

    # Initialize Client
    client = GraphService.get_client()

    if not GraphService.is_connected(client):
        st.warning("⚠️ Could not connect to Neo4j. Using mock mode or check credentials.")
        st.info("Displaying static example data.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🧬 Gene")
            st.code("CYP2C19")
        with col2:
            st.markdown("### 💊 Associated Drugs")
            st.write("- Clopidogrel (Metabolism)")
            st.write("- Omeprazole (Metabolism)")
            
    else:
        # Real KG Interaction
        tab1, tab2 = st.tabs(["Search", "Statistics"])
        
        with tab1:
            st.markdown("### 🔍 Search Graph")
            query_type = st.selectbox("Search For", ["Gene", "Drug", "Variant"])
            query = st.text_input(f"Enter {query_type} Name/ID")
            
            if st.button("Search"):
                st.info(f"Searching for {query}...")
                st.write("No results found (Mock implementation)")
                
        with tab2:
            st.markdown("### 📈 Graph Statistics")
            try:
                stats = client.get_statistics() if hasattr(client, 'get_statistics') else {"Nodes": 0, "Edges": 0}
                st.json(stats)
            except Exception as e:
                st.error(f"Error fetching stats: {e}")

    render_footer()

if __name__ == "__main__":
    render_knowledge_graph()
