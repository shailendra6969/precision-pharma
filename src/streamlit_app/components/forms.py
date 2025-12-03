import streamlit as st
from typing import Dict, Any

def patient_input_form() -> Dict[str, Any]:
    """Render standardized patient input form."""
    with st.form("patient_form"):
        st.markdown("### 👤 Patient Profile")
        name = st.text_input("Patient Name", placeholder="e.g. John Doe")
        col1, col2, col3 = st.columns(3)
        with col1:
            age = st.number_input("Age", min_value=0, max_value=120, value=45)
        with col2:
            sex = st.selectbox("Sex", ["Male", "Female", "Other"])
        with col3:
            renal = st.selectbox("Renal Function", ["Normal", "Impaired", "Failure"])
            
        st.markdown("### 💊 Medication")
        
        search_mode = st.toggle("🔍 Search Online (Live FDA Database)", value=False)
        
        if search_mode:
            from src.pipeline.external_apis import OpenFDAClient
            client = OpenFDAClient()
            
            search_query = st.text_input("Search Drug Name", placeholder="Type to search (e.g. 'advil')")
            
            if search_query and len(search_query) >= 3:
                with st.spinner("Searching FDA database..."):
                    suggestions = client.search_drugs(search_query)
                    if suggestions:
                        drug = st.selectbox("Select Found Drug", suggestions)
                    else:
                        st.warning("No drugs found. Try a different name.")
                        drug = None
            else:
                st.info("Enter at least 3 characters to search.")
                drug = None
        else:
            from src.streamlit_app.assets.drug_list import COMMON_DRUGS
            drug = st.selectbox("Select Drug", COMMON_DRUGS, index=COMMON_DRUGS.index("Warfarin") if "Warfarin" in COMMON_DRUGS else 0)
        
        submitted = st.form_submit_button("Predict Risk")
        
        if submitted:
            return {
                "name": name,
                "age": age,
                "sex": sex,
                "renal": renal,
                "drug": drug,
                "submitted": True
            }
    return {"submitted": False}
