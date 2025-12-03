"""
Core predictive models for drug response and ADR risk prediction.
Includes XGBoost models with SHAP explainability.
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any, List, Optional
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
try:
    import xgboost as xgb
except Exception:
    xgb = None

try:
    import lightgbm as lgb
except Exception:
    lgb = None

from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
import logging

logger = logging.getLogger(__name__)


class DrugResponsePredictor:
    """
    Predict drug effectiveness based on patient genotype.
    Models drug response as a binary classification problem.
    """
    
    def __init__(self, model_type: str = 'xgboost'):
        """Initialize predictor with specified model type."""
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = None
        self.is_fitted = False
    
    def prepare_data(self, X: pd.DataFrame, y: pd.Series = None) -> Tuple[np.ndarray, pd.Series]:
        """Prepare and scale feature matrix."""
        self.feature_names = X.columns.tolist()
        X_scaled = self.scaler.fit_transform(X)
        return X_scaled, y
    
    def train(self, X: pd.DataFrame, y: pd.Series, **kwargs):
        """
        Train the model on labeled data.
        
        Args:
            X: Feature matrix (samples x features)
            y: Binary labels (0: no response, 1: good response)
        """
        X_scaled, y = self.prepare_data(X, y)
        
        if self.model_type == 'xgboost':
            if xgb is None:
                logger.warning("XGBoost not available, falling back to sklearn GradientBoosting")
                self.model = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=6, random_state=42)
            else:
                params = {
                    'objective': 'binary:logistic',
                    'max_depth': 6,
                    'learning_rate': 0.1,
                    'n_estimators': 100,
                    'random_state': 42,
                }
                params.update(kwargs)
                self.model = xgb.XGBClassifier(**params)
        elif self.model_type == 'lightgbm':
            if lgb is None:
                logger.warning("LightGBM not available, falling back to sklearn GradientBoosting")
                self.model = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=6, random_state=42)
            else:
                params = {
                    'objective': 'binary',
                    'max_depth': 6,
                    'learning_rate': 0.1,
                    'n_estimators': 100,
                    'random_state': 42,
                }
                params.update(kwargs)
                self.model = lgb.LGBMClassifier(**params)
        elif self.model_type == 'sklearn':
             self.model = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=6, random_state=42)
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
        
        self.model.fit(X_scaled, y)
        self.is_fitted = True
        logger.info(f"Trained {self.model_type} model for drug response prediction")
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict drug response probabilities."""
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call train() first.")
        
        X_scaled = self.scaler.transform(X)
        return self.model.predict_proba(X_scaled)[:, 1]
    
    def get_feature_importance(self, top_k: int = 10) -> Dict[str, float]:
        """Get top k most important features."""
        if not self.is_fitted:
            raise ValueError("Model not fitted.")
        
        importances = self.model.feature_importances_
        feature_importance = dict(zip(self.feature_names, importances))
        return dict(sorted(feature_importance.items(), 
                          key=lambda x: x[1], reverse=True)[:top_k])


class ADRRiskPredictor:
    """
    Predict adverse drug reaction (ADR) risk.
    Multimodal: combines genotype + clinical features.
    """
    
    def __init__(self, model_type: str = 'xgboost'):
        """Initialize ADR risk predictor."""
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = None
        self.is_fitted = False
    
    def prepare_data(self, X: pd.DataFrame, y: pd.Series = None) -> Tuple[np.ndarray, pd.Series]:
        """Prepare feature matrix with clinical + genomic features."""
        self.feature_names = X.columns.tolist()
        X_scaled = self.scaler.fit_transform(X)
        return X_scaled, y
    
    def train(self, X: pd.DataFrame, y: pd.Series, **kwargs):
        """
        Train ADR risk prediction model.
        
        Args:
            X: Feature matrix (genomic + clinical)
            y: Binary ADR outcome (0: no ADR, 1: ADR occurred)
        """
        X_scaled, y = self.prepare_data(X, y)
        
        if self.model_type == 'xgboost':
            if xgb is None:
                logger.warning("XGBoost not available, falling back to sklearn GradientBoosting")
                self.model = GradientBoostingClassifier(n_estimators=150, learning_rate=0.05, max_depth=7, random_state=42)
            else:
                params = {
                    'objective': 'binary:logistic',
                    'max_depth': 7,
                    'learning_rate': 0.05,
                    'n_estimators': 150,
                    'random_state': 42,
                    'scale_pos_weight': (y == 0).sum() / (y == 1).sum(),  # Handle imbalance
                }
                params.update(kwargs)
                self.model = xgb.XGBClassifier(**params)
        elif self.model_type == 'lightgbm':
            if lgb is None:
                logger.warning("LightGBM not available, falling back to sklearn GradientBoosting")
                self.model = GradientBoostingClassifier(n_estimators=150, learning_rate=0.05, max_depth=7, random_state=42)
            else:
                params = {
                    'objective': 'binary',
                    'max_depth': 7,
                    'learning_rate': 0.05,
                    'n_estimators': 150,
                    'random_state': 42,
                }
                params.update(kwargs)
                self.model = lgb.LGBMClassifier(**params)
        elif self.model_type == 'sklearn':
             self.model = GradientBoostingClassifier(n_estimators=150, learning_rate=0.05, max_depth=7, random_state=42)
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
        
        self.model.fit(X_scaled, y)
        self.is_fitted = True
        logger.info(f"Trained {self.model_type} model for ADR risk prediction")
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict ADR risk probabilities (0-1)."""
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call train() first.")
        
        X_scaled = self.scaler.transform(X)
        return self.model.predict_proba(X_scaled)[:, 1]
    
    def risk_category(self, proba: float) -> str:
        """Categorize risk into low/medium/high."""
        if proba < 0.33:
            return 'low'
        elif proba < 0.67:
            return 'medium'
        else:
            return 'high'
    
    def get_feature_importance(self, top_k: int = 10) -> Dict[str, float]:
        """Get top k most important features."""
        if not self.is_fitted:
            raise ValueError("Model not fitted.")
        
        importances = self.model.feature_importances_
        feature_importance = dict(zip(self.feature_names, importances))
        return dict(sorted(feature_importance.items(), 
                          key=lambda x: x[1], reverse=True)[:top_k])


class PathogenicityClassifier:
    """
    Classify genetic variants as:
    - Benign
    - Likely Benign
    - Pathogenic
    - Likely Pathogenic
    """
    
    def __init__(self):
        """Initialize pathogenicity classifier."""
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = None
        self.is_fitted = False
        self.classes = ['benign', 'likely_benign', 'likely_pathogenic', 'pathogenic']
    
    def prepare_data(self, X: pd.DataFrame) -> np.ndarray:
        """Prepare features."""
        self.feature_names = X.columns.tolist()
        return self.scaler.fit_transform(X)
    
    def train(self, X: pd.DataFrame, y: pd.Series, **kwargs):
        """
        Train multi-class pathogenicity classifier.
        
        Args:
            X: Variant features
            y: Classification labels
        """
        X_scaled = self.prepare_data(X)
        
        if xgb is None:
            logger.warning("XGBoost not available, falling back to sklearn GradientBoosting")
            self.model = GradientBoostingClassifier(n_estimators=200, learning_rate=0.1, max_depth=8, random_state=42)
        else:
            params = {
                'objective': 'multi:softprob',
                'num_class': len(self.classes),
                'max_depth': 8,
                'learning_rate': 0.1,
                'n_estimators': 200,
                'random_state': 42,
            }
            params.update(kwargs)
            self.model = xgb.XGBClassifier(**params)
        self.model.fit(X_scaled, y)
        self.is_fitted = True
        logger.info("Trained pathogenicity classifier")
    
    def predict(self, X: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict pathogenicity class and confidence scores.
        
        Returns:
            predictions: class labels
            probabilities: confidence scores for each class
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call train() first.")
        
        X_scaled = self.scaler.transform(X)
        proba = self.model.predict_proba(X_scaled)
        predictions = self.model.predict(X_scaled)
        
        return predictions, proba
    
    def predict_proba_dict(self, X: pd.DataFrame) -> pd.DataFrame:
        """Return probabilities as DataFrame with class names."""
        if not self.is_fitted:
            raise ValueError("Model not fitted.")
        
        X_scaled = self.scaler.transform(X)
        proba = self.model.predict_proba(X_scaled)
        
        return pd.DataFrame(
            proba,
            columns=self.classes
        )


def create_synthetic_training_data(n_samples: int = 500) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Generate synthetic training data for demonstration.
    In production, use real labeled data from ClinVar, PharmGKB, etc.
    """
    np.random.seed(42)
    
    # Create features
    features = {
        'is_drug_metabolizer': np.random.binomial(1, 0.3, n_samples),
        'cadd_score': np.random.uniform(0, 35, n_samples),
        'allele_frequency': np.random.exponential(0.05, n_samples),
        'conservation_score': np.random.uniform(0, 1, n_samples),
        'effect_missense': np.random.binomial(1, 0.4, n_samples),
        'effect_nonsense': np.random.binomial(1, 0.1, n_samples),
        'is_pathogenic': np.random.binomial(1, 0.2, n_samples),
    }
    
    X = pd.DataFrame(features)
    
    # Generate synthetic labels (ADR risk) based on features
    # Higher CADD, pathogenic variants, drug metabolizers → higher risk
    y = (
        (X['cadd_score'] > 20).astype(int) * 0.3 +
        X['is_pathogenic'] * 0.4 +
        (X['allele_frequency'] < 0.01).astype(int) * 0.2 +
        (X['is_drug_metabolizer'] & (X['effect_missense'] > 0)).astype(int) * 0.1
    )
    
    # Binarize with threshold
    y = (y > 0.5).astype(int)
    
    return X, y
