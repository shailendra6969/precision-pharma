import pytest
import pandas as pd
import numpy as np
from src.models.predictors import ADRRiskPredictor, DrugResponsePredictor, create_synthetic_training_data

@pytest.fixture
def synthetic_data():
    return create_synthetic_training_data(n_samples=50)

def test_adr_predictor(synthetic_data):
    X, y = synthetic_data
    model = ADRRiskPredictor(model_type='xgboost')
    model.train(X, y)
    
    assert model.is_fitted
    
    # Test prediction
    sample = X.iloc[:1]
    prob = model.predict(sample)[0]
    assert 0 <= prob <= 1
    
    # Test risk category
    cat = model.risk_category(prob)
    assert cat in ['low', 'medium', 'high']

def test_drug_response_predictor(synthetic_data):
    X, y = synthetic_data
    model = DrugResponsePredictor(model_type='xgboost')
    model.train(X, y)
    
    assert model.is_fitted
    
    # Test prediction
    sample = X.iloc[:1]
    prob = model.predict(sample)[0]
    assert 0 <= prob <= 1
