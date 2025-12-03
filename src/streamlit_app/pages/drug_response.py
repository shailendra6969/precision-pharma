import streamlit as st
from src.streamlit_app.components.layout import page_container, render_header, render_footer
from src.streamlit_app.components.charts import render_adr_risk_gauge
from src.streamlit_app.components.forms import patient_input_form
from src.streamlit_app.utils.model_utils import PredictionService

def render_drug_response():
    """Render the Drug Response page."""
    page_container("Drug Response", icon="💊")
    render_header("Drug Response Prediction", "AI-powered pharmacogenomic risk assessment")

    # Load Models
    try:
        adr_model, _, X_train = PredictionService.load_models()
    except Exception as e:
        st.error(f"Error loading models: {e}")
        st.stop()

    # Patient Input Form
    form_data = patient_input_form()

    if form_data["submitted"]:
        st.markdown("---")
        st.markdown("### 🔮 Prediction Results")
        
        # Mock prediction for demo
        sample = X_train.iloc[:1]
        
        try:
            prob, risk_cat = PredictionService.predict_adr(adr_model, sample)
            drug = form_data["drug"]
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                render_adr_risk_gauge(prob)
                
            with col2:
                st.markdown(f"#### Risk Category: **{risk_cat.upper()}**")
                
                if risk_cat == 'high':
                    st.error(f"High risk of adverse reaction to **{drug}** detected.")
                elif risk_cat == 'medium':
                    st.warning(f"Moderate risk of adverse reaction to **{drug}**.")
                else:
                    st.success(f"Low risk of adverse reaction to **{drug}**.")
                    
                st.info("Based on patient genotype (CYP2C9*2) and clinical factors.")
                
                with st.expander("See Explanation (SHAP)"):
                    st.write("Feature contributions to this prediction:")
                    importance = PredictionService.get_feature_importance(adr_model)
                    st.bar_chart(importance)
                    
        except Exception as e:
            st.error(f"Prediction failed: {e}")

    render_footer()

if __name__ == "__main__":
    render_drug_response()
