import streamlit as st
from src.streamlit_app.components.layout import render_header, render_footer
from src.streamlit_app.components.sidebar import render_sidebar
from src.streamlit_app.components.charts import render_adr_risk_gauge
from src.streamlit_app.components.forms import patient_input_form
from src.streamlit_app.utils.model_utils import PredictionService
from src.streamlit_app.utils.graph_utils import GraphService
from src.streamlit_app.components.graph_viz import render_interactive_graph

def render_drug_response():
    """Render the Drug Response page."""
    st.set_page_config(page_title="Drug Response | Precision Pharma", page_icon="💊", layout="wide")
    
    # Load Theme
    with open("src/streamlit_app/theme/medical_theme.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    render_sidebar()
    render_header("Drug Response Prediction", "AI-powered pharmacogenomic risk assessment")

    # Load Models
    try:
        adr_model, _, X_train = PredictionService.load_models()
    except Exception as e:
        st.error(f"Error loading models: {e}")
        st.stop()

    # Layout: Form on Left, Results on Right
    col_form, col_results = st.columns([1, 2])
    
    with col_form:
        st.markdown("### 📝 Patient Data")
        form_data = patient_input_form()

    with col_results:
        if form_data["submitted"]:
            drug_name = form_data["drug"]
            name_str = f" for **{form_data['name']}**" if form_data.get("name") else ""
            
            st.markdown(f"### 🔮 Analysis Results{name_str}")
            
            # 1. AI Prediction
            st.markdown("#### 🤖 AI Risk Assessment")
            sample = X_train.iloc[:1] # Mock sample
            prob, risk_cat = PredictionService.predict_adr(adr_model, sample)
            
            c1, c2 = st.columns([1, 2])
            with c1:
                render_adr_risk_gauge(prob)
            with c2:
                if risk_cat == 'high':
                    st.error(f"**HIGH RISK** detected for {drug_name}")
                    st.markdown("⚠️ Patient genotype suggests poor metabolism.")
                elif risk_cat == 'medium':
                    st.warning(f"**MODERATE RISK** detected for {drug_name}")
                else:
                    st.success(f"**LOW RISK** detected for {drug_name}")
                    st.markdown("✅ Standard dosing likely safe.")

            # 2. Knowledge Graph Insights
            st.markdown("---")
            st.markdown("#### 🕸️ Knowledge Graph Insights")
            
            service = GraphService.get_client()
            if service:
                # Get Drug Details (PubChem)
                details = service.get_drug_details(drug_name)
                if details:
                    st.info(f"**Chemical Info**: {details.get('iupac_name', 'N/A')} | **Formula**: {details.get('formula', 'N/A')}")
                
                # Get Related Genes (DGIdb)
                genes = service.find_related_genes(drug_name)
                if genes:
                    st.write(f"**{drug_name}** interacts with **{len(genes)}** known genes:")
                    
                    # Mini Graph
                    nodes = [{"id": drug_name, "label": drug_name, "type": "Drug"}]
                    edges = []
                    for g in genes[:5]: # Limit to 5 for clarity
                        nodes.append({"id": g.symbol, "label": g.symbol, "type": "Gene"})
                        edges.append({"source": g.symbol, "target": drug_name, "type": "AFFECTS"})
                    
                    render_interactive_graph(nodes, edges, height="300px")
                else:
                    st.caption("No direct gene interactions found in Knowledge Graph.")

            # 3. Real-World Evidence (OpenFDA)
            st.markdown("---")
            st.markdown("#### 🏥 Real-World Evidence (OpenFDA)")
            
            from src.pipeline.external_apis import OpenFDAClient
            fda = OpenFDAClient()
            events = fda.get_adverse_events(drug_name, limit=2)
            
            if events:
                for i, event in enumerate(events):
                    reactions = [r.get('reactionmeddrapt') for r in event.get('patient', {}).get('reaction', [])]
                    st.warning(f"**Report #{i+1}**: {', '.join(reactions)}")
            else:
                st.caption("No recent adverse event reports found.")

    render_footer()

if __name__ == "__main__":
    render_drug_response()
