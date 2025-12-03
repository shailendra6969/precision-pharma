import streamlit as st
from typing import Dict, Any

def patient_input_form() -> Dict[str, Any]:
    """Render standardized patient input form."""
    with st.form("patient_form"):
        st.markdown("### 👤 Patient Profile")
        col1, col2, col3 = st.columns(3)
        with col1:
            age = st.number_input("Age", min_value=0, max_value=120, value=45)
        with col2:
            sex = st.selectbox("Sex", ["Male", "Female", "Other"])
        with col3:
            renal = st.selectbox("Renal Function", ["Normal", "Impaired", "Failure"])
            
        st.markdown("### 💊 Medication")
        drug = st.selectbox("Select Drug", ["Warfarin", "Clopidogrel", "Simvastatin", "Codeine"])
        
        submitted = st.form_submit_button("Predict Risk")
        
        if submitted:
            return {
                "age": age,
                "sex": sex,
                "renal": renal,
                "drug": drug,
                "submitted": True
            }
    return {"submitted": False}
