import streamlit as st
import pandas as pd
from src.models.predictors import ADRRiskPredictor, DrugResponsePredictor, create_synthetic_training_data

class PredictionService:
    """Service for running predictive models."""
    
    @staticmethod
    @st.cache_resource
    def load_models():
        """Load or initialize models."""
        # In a real app, load from disk. Here we train on synthetic data.
        X, y = create_synthetic_training_data(n_samples=200)
        
        adr_model = ADRRiskPredictor(model_type='xgboost')
        adr_model.train(X, y)
        
        response_model = DrugResponsePredictor(model_type='xgboost')
        response_model.train(X, y)
        
        return adr_model, response_model, X

    @staticmethod
    def predict_adr(model, patient_data: pd.DataFrame):
        """Run ADR prediction."""
        prob = model.predict(patient_data)[0]
        category = model.risk_category(prob)
        return prob, category

    @staticmethod
    def get_feature_importance(model):
        """Get feature importance for visualization."""
        return model.get_feature_importance()
