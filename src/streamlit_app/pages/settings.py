import streamlit as st
import os
from src.streamlit_app.components.layout import page_container, render_header, render_footer
from src.streamlit_app.utils.health_check import SystemHealthCheck
from src.streamlit_app.utils.config import VERSION
from dotenv import load_dotenv, set_key

# Load env vars
load_dotenv()
ENV_PATH = os.path.join(os.getcwd(), ".env")

def render_settings():
    """Render the Settings page."""
    page_container("Settings", icon="⚙️")
    render_header("System Control Center", "Manage configuration, health, and data.")

    tab1, tab2, tab3 = st.tabs(["📊 System Health", "⚙️ Configuration", "💾 Database & Cache"])

    # --- TAB 1: System Health ---
    with tab1:
        st.markdown("### Service Status")
        if st.button("🔄 Refresh Status"):
            st.rerun()
            
        with st.spinner("Checking services..."):
            health_data = SystemHealthCheck.run_all_checks()
            
        for service, status in health_data.items():
            col1, col2, col3 = st.columns([3, 1, 2])
            with col1:
                st.write(f"**{service}**")
            with col2:
                if status["status"] == "online":
                    st.success("Online")
                elif status["status"] == "degraded":
                    st.warning("Degraded")
                else:
                    st.error("Offline")
            with col3:
                st.caption(f"{status['latency']} | {status['details']}")
            st.divider()

    # --- TAB 2: Configuration ---
    with tab2:
        st.markdown("### 🔐 Environment Variables")
        st.info("Update your API keys and database credentials here. Changes require a restart.")
        
        with st.form("config_form"):
            neo4j_uri = st.text_input("Neo4j URI", value=os.getenv("NEO4J_URI", ""))
            neo4j_user = st.text_input("Neo4j User", value=os.getenv("NEO4J_USER", ""))
            neo4j_pass = st.text_input("Neo4j Password", value=os.getenv("NEO4J_PASSWORD", ""), type="password")
            clinvar_email = st.text_input("ClinVar Email", value=os.getenv("CLINVAR_API_EMAIL", ""))
            openai_key = st.text_input("OpenAI API Key", value=os.getenv("OPENAI_API_KEY", ""), type="password")
            
            st.markdown("#### 🌐 External APIs")
            openfda_url = st.text_input("OpenFDA Label URL", value=os.getenv("OPENFDA_LABEL_URL", "https://api.fda.gov/drug/label.json"))
            mygene_url = st.text_input("MyGene.info URL", value=os.getenv("MYGENE_URL", "https://mygene.info/v3/query"))
            dgidb_url = st.text_input("DGIdb URL", value=os.getenv("DGIDB_URL", "https://dgidb.org/api/graphql"))
            pubchem_url = st.text_input("PubChem URL", value=os.getenv("PUBCHEM_URL", "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name"))

            if st.form_submit_button("Save Configuration"):
                try:
                    set_key(ENV_PATH, "NEO4J_URI", neo4j_uri)
                    set_key(ENV_PATH, "NEO4J_USER", neo4j_user)
                    set_key(ENV_PATH, "NEO4J_PASSWORD", neo4j_pass)
                    set_key(ENV_PATH, "CLINVAR_API_EMAIL", clinvar_email)
                    set_key(ENV_PATH, "OPENAI_API_KEY", openai_key)
                    
                    set_key(ENV_PATH, "OPENFDA_LABEL_URL", openfda_url)
                    set_key(ENV_PATH, "MYGENE_URL", mygene_url)
                    set_key(ENV_PATH, "DGIDB_URL", dgidb_url)
                    set_key(ENV_PATH, "PUBCHEM_URL", pubchem_url)
                    
                    st.success("Configuration saved! Please restart the app to apply changes.")
                except Exception as e:
                    st.error(f"Failed to save .env: {e}")

    # --- TAB 3: Database & Cache ---
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🧹 Cache Management")
            st.write("Clear application cache to force reload of data and connections.")
            if st.button("Clear App Cache"):
                st.cache_data.clear()
                st.cache_resource.clear()
                st.success("Cache cleared successfully!")
                
        with col2:
            st.markdown("### 🛠️ Database Tools")
            st.write("Manage your Neo4j data.")
            if st.button("🌱 Seed Demo Data"):
                with st.spinner("Seeding database..."):
                    from src.streamlit_app.utils.graph_utils import GraphService
                    client = GraphService.get_client()
                    if client:
                        from src.kg.knowledge_graph import ingest_mock_data
                        ingest_mock_data(client)
                        st.success("Database seeded!")
                    else:
                        st.error("Could not connect to Neo4j.")

    st.markdown("---")
    st.caption(f"Precision Pharma AI Platform v{VERSION} | Built with Streamlit & Neo4j")
    render_footer()

if __name__ == "__main__":
    render_settings()
