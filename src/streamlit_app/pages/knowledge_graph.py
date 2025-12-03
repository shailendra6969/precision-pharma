import streamlit as st
import os
from src.streamlit_app.components.layout import page_container, render_header, render_footer
from src.kg.service import GraphService
from src.streamlit_app.components.graph_viz import render_interactive_graph

# Initialize Service (Singleton pattern via cache)
@st.cache_resource
def get_graph_service():
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")
    return GraphService(uri, user, password)

def render_health_widget(service: GraphService):
    """Render KG health status."""
    stats = service.get_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Nodes", stats.node_count)
    with col2:
        st.metric("Edges", stats.edge_count)
    with col3:
        st.metric("Latency", f"{stats.latency_ms:.2f}ms")
    with col4:
        status_color = "🟢" if stats.is_connected else "🔴"
        st.markdown(f"### Status: {status_color}")
        if not stats.is_connected:
            st.caption("Using Mock Data")

def render_knowledge_graph():
    """Render the Knowledge Graph page."""
    page_container("Knowledge Graph 2.0", icon="🕸️")
    render_header("Knowledge Graph Explorer", "Enterprise Clinical Data Graph")

    service = get_graph_service()
    render_health_widget(service)
    
    st.markdown("---")

    tab1, tab2 = st.tabs(["🔍 Search & Explore", "🛠️ Management"])

    with tab1:
        col1, col2 = st.columns([1, 3])
        with col1:
            query_type = st.selectbox("Entity Type", ["Gene", "Drug"])
        with col2:
            query = st.text_input("Search Term", placeholder="e.g. CYP2C19 or Warfarin")

        if query:
            with st.spinner(f"Searching for {query}..."):
                if query_type == "Gene":
                    gene = service.search_gene(query)
                    if gene:
                        is_external = gene.id.startswith("external_")
                        source_label = "🌍 External Database (MyGene.info)" if is_external else "🏠 Local Knowledge Graph"
                        
                        st.success(f"Found Gene: {gene.symbol}")
                        st.caption(f"Source: {source_label}")
                        st.json(gene.model_dump())
                        
                        # Find related drugs (Local + External)
                        drugs = service.find_related_drugs(gene.symbol)
                        
                        if drugs:
                            st.subheader(f"Related Drugs ({len(drugs)})")
                            if is_external:
                                st.caption("💊 Sourced from DGIdb (Drug Gene Interaction Database)")
                            
                            # Prepare graph data
                            nodes = [{"id": gene.symbol, "label": gene.symbol, "type": "Gene"}]
                            edges = []
                            for drug in drugs:
                                nodes.append({"id": drug.name, "label": drug.name, "type": "Drug"})
                                edges.append({"source": gene.symbol, "target": drug.name, "type": "AFFECTS"})
                            
                            render_interactive_graph(nodes, edges)
                            
                            with st.expander("View Drug Details"):
                                # Enhance with PubChem data for the first few drugs to avoid rate limits
                                enriched_drugs = []
                                for d in drugs[:5]: # Limit to 5 for performance
                                    details = service.get_drug_details(d.name)
                                    drug_data = d.model_dump()
                                    if details:
                                        drug_data.update(details)
                                    enriched_drugs.append(drug_data)
                                    
                                st.dataframe(enriched_drugs)
                        else:
                            st.info("No known drug interactions found for this gene.")
                            if is_external:
                                if st.button("➕ Add to Knowledge Graph"):
                                     st.toast(f"Added {gene.symbol} to ingestion queue (Demo)")
                    else:
                        st.warning("Gene not found in local graph or external databases.")
                        
                elif query_type == "Drug":
                    drug = service.search_drug(query)
                    if drug:
                        is_external = drug.id.startswith("external_")
                        source_label = "🌍 External Database (OpenFDA)" if is_external else "🏠 Local Knowledge Graph"
                        
                        st.success(f"Found Drug: {drug.name}")
                        if drug.properties.get('generic_name'):
                            st.info(f"Active Ingredient: **{drug.properties['generic_name']}**")
                        st.caption(f"Source: {source_label}")
                        
                        # Fetch and merge PubChem details
                        details = service.get_drug_details(drug.name)
                        drug_data = drug.model_dump()
                        if details:
                            drug_data.update(details)
                        st.json(drug_data)
                        
                        # Find related genes
                        genes = service.find_related_genes(drug.name)
                        
                        if genes:
                            st.subheader(f"Associated Genes ({len(genes)})")
                            if is_external:
                                st.caption("🧬 Sourced from DGIdb")
                                
                            # Prepare graph data
                            nodes = [{"id": drug.name, "label": drug.name, "type": "Drug"}]
                            edges = []
                            for gene in genes:
                                nodes.append({"id": gene.symbol, "label": gene.symbol, "type": "Gene"})
                                edges.append({"source": gene.symbol, "target": drug.name, "type": "AFFECTS"})
                            
                            render_interactive_graph(nodes, edges)
                            
                            with st.expander("View Gene Details"):
                                st.table([g.model_dump() for g in genes])
                        else:
                            st.info("No associated genes found.")
                    else:
                        st.warning("Drug not found in local graph or external databases.")

    with tab2:
        st.markdown("### Database Operations")
        if st.button("🔄 Reconnect"):
            st.cache_resource.clear()
            st.rerun()
            
        if st.button("🌱 Seed Demo Data"):
            # Call legacy ingest or new seeder
            st.info("Seeding initiated...")

    render_footer()

if __name__ == "__main__":
    render_knowledge_graph()
