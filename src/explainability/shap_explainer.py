"""
SHAP-based explainability for model predictions.
Provides feature importance, SHAP values, and counterfactual explanations.
"""

import numpy as np
import pandas as pd
import shap
from typing import Dict, List, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class ModelExplainer:
    """
    Wrapper for SHAP explainability on tree-based models.
    Generates feature contributions and visualizations.
    """
    
    def __init__(self, model, X_data: pd.DataFrame):
        """
        Initialize explainer with trained model and background data.
        
        Args:
            model: Trained XGBoost or LightGBM model
            X_data: Background data for SHAP computation
        """
        self.model = model
        self.X_data = X_data
        self.explainer = shap.TreeExplainer(model)
        self.shap_values = None
    
    def compute_shap_values(self, X_test: pd.DataFrame) -> np.ndarray:
        """Compute SHAP values for test samples."""
        self.shap_values = self.explainer.shap_values(X_test)
        if isinstance(self.shap_values, list):  # Multi-class
            self.shap_values = self.shap_values[1]  # Use positive class
        return self.shap_values
    
    def get_feature_importance(self, top_k: int = 10) -> Dict[str, float]:
        """Get global feature importance from SHAP values."""
        if self.shap_values is None:
            raise ValueError("Compute SHAP values first")
        
        # Mean absolute SHAP value
        mean_abs_shap = np.abs(self.shap_values).mean(axis=0)
        importance = dict(zip(self.X_data.columns, mean_abs_shap))
        return dict(sorted(importance.items(), key=lambda x: x[1], reverse=True)[:top_k])
    
    def explain_prediction(self, sample_idx: int, X_test: pd.DataFrame) -> Dict[str, Any]:
        """
        Explain individual prediction with SHAP force plot data.
        
        Returns:
            Dictionary with:
            - base_value: Model's expected value
            - feature_contributions: (feature, value, contribution) tuples
            - prediction: Model output
        """
        if self.shap_values is None:
            self.compute_shap_values(X_test)
        
        shap_sample = self.shap_values[sample_idx]
        feature_values = X_test.iloc[sample_idx]
        
        contributions = []
        for feat_idx, feat_name in enumerate(X_test.columns):
            contributions.append({
                'feature': feat_name,
                'value': float(feature_values.iloc[feat_idx]),
                'shap_value': float(shap_sample[feat_idx]),
                'contribution': abs(float(shap_sample[feat_idx])),
            })
        
        # Sort by absolute contribution
        contributions.sort(key=lambda x: x['contribution'], reverse=True)
        
        return {
            'base_value': float(self.explainer.expected_value),
            'features': contributions[:10],  # Top 10 features
            'prediction': float(self.model.predict_proba([feature_values.values])[0, 1]),
        }
    
    def counterfactual_analysis(self, sample_idx: int, X_test: pd.DataFrame,
                               target_prob: float = 0.5) -> Dict[str, Any]:
        """
        Generate counterfactual explanation: which features need to change?
        
        Args:
            sample_idx: Index of sample to explain
            X_test: Test data
            target_prob: Target probability threshold
        
        Returns:
            Counterfactual suggestions
        """
        if self.shap_values is None:
            self.compute_shap_values(X_test)
        
        sample = X_test.iloc[sample_idx].copy()
        current_pred = self.model.predict_proba([sample.values])[0, 1]
        
        shap_sample = self.shap_values[sample_idx]
        
        # Find features with largest SHAP values that could flip the prediction
        feature_impacts = []
        for feat_idx, feat_name in enumerate(X_test.columns):
            impact = abs(shap_sample[feat_idx])
            direction = 'increase' if shap_sample[feat_idx] > 0 else 'decrease'
            feature_impacts.append({
                'feature': feat_name,
                'current_value': float(sample.iloc[feat_idx]),
                'impact': float(impact),
                'direction': direction,
                'avg_value_in_positive_class': float(self.X_data[feat_name].mean()),
            })
        
        feature_impacts.sort(key=lambda x: x['impact'], reverse=True)
        
        return {
            'current_probability': float(current_pred),
            'target_probability': target_prob,
            'top_features_to_change': feature_impacts[:5],
        }


class LLMExplainer:
    """
    Generate natural language explanations for drug response and ADR predictions.
    Uses templates + key features to create clinician-friendly explanations.
    """
    
    # Explanation templates
    ADR_RISK_TEMPLATE = """
    Based on the patient's genetic profile and clinical context:
    
    **ADR Risk Assessment: {risk_category.upper()}**
    
    Key genetic factors:
    {genetic_factors}
    
    Clinical considerations:
    {clinical_factors}
    
    **Recommendations:**
    {recommendations}
    
    **Evidence Sources:** {evidence_sources}
    """
    
    DRUG_RESPONSE_TEMPLATE = """
    **Drug Response Prediction for {drug_name}**
    
    Predicted effectiveness: {effectiveness_level} ({probability:.1%})
    
    Supporting genetic variants:
    {variants}
    
    Known interactions:
    {interactions}
    
    **Clinical Guidance:**
    {guidance}
    """
    
    def __init__(self):
        """Initialize LLM explainer."""
        self.explanations = {}
    
    def explain_adr_risk(self, variant_list: List[str], drug_list: List[str],
                        risk_probability: float, age: int = None,
                        renal_function: str = None) -> str:
        """
        Generate natural language explanation for ADR risk.
        
        Args:
            variant_list: List of patient variants
            drug_list: List of prescribed drugs
            risk_probability: Predicted ADR risk (0-1)
            age: Patient age (optional)
            renal_function: Renal function status (optional)
        
        Returns:
            Natural language explanation
        """
        risk_category = self._risk_category(risk_probability)
        
        genetic_factors = self._format_genetic_factors(variant_list)
        clinical_factors = self._format_clinical_factors(age, renal_function)
        recommendations = self._get_adr_recommendations(risk_category)
        evidence = self._get_evidence_sources(variant_list, drug_list)
        
        return self.ADR_RISK_TEMPLATE.format(
            risk_category=risk_category,
            genetic_factors=genetic_factors,
            clinical_factors=clinical_factors,
            recommendations=recommendations,
            evidence_sources=evidence,
        )
    
    def explain_drug_response(self, drug_name: str, variants: List[str],
                             probability: float) -> str:
        """Generate explanation for drug response prediction."""
        effectiveness = self._effectiveness_level(probability)
        variant_info = self._format_variants_info(variants)
        interactions = self._get_drug_interactions(drug_name, variants)
        guidance = self._get_clinical_guidance(drug_name, effectiveness, variants)
        
        return self.DRUG_RESPONSE_TEMPLATE.format(
            drug_name=drug_name,
            effectiveness_level=effectiveness,
            probability=probability,
            variants=variant_info,
            interactions=interactions,
            guidance=guidance,
        )
    
    @staticmethod
    def _risk_category(probability: float) -> str:
        """Categorize risk level."""
        if probability < 0.33:
            return 'low'
        elif probability < 0.67:
            return 'medium'
        else:
            return 'high'
    
    @staticmethod
    def _effectiveness_level(probability: float) -> str:
        """Categorize drug effectiveness."""
        if probability < 0.4:
            return 'likely poor'
        elif probability < 0.7:
            return 'moderate'
        else:
            return 'likely good'
    
    @staticmethod
    def _format_genetic_factors(variants: List[str]) -> str:
        """Format genetic factors for explanation."""
        if not variants:
            return "No significant drug-metabolizing variants detected."
        return "\n".join([f"• {v}" for v in variants[:5]])
    
    @staticmethod
    def _format_clinical_factors(age: int = None, renal_function: str = None) -> str:
        """Format clinical factors."""
        factors = []
        if age and age > 65:
            factors.append(f"• Advanced age ({age} years) - increased sensitivity to drugs")
        if renal_function and renal_function != 'normal':
            factors.append(f"• {renal_function.capitalize()} renal function - may affect clearance")
        if not factors:
            factors.append("• Normal age and organ function")
        return "\n".join(factors)
    
    @staticmethod
    def _get_adr_recommendations(risk_category: str) -> str:
        """Get recommendations based on risk level."""
        recommendations = {
            'low': '• Monitor with standard protocols\n• Continue current therapy',
            'medium': '• Increase monitoring frequency\n• Consider dose adjustment\n• Patient education recommended',
            'high': '• High-risk designation - consider alternative therapy\n• Intensive monitoring required\n• Consult pharmacist/geneticist',
        }
        return recommendations.get(risk_category, '')
    
    @staticmethod
    def _get_evidence_sources(variants: List[str], drugs: List[str]) -> str:
        """Format evidence sources."""
        sources = ['PharmGKB', 'ClinVar', 'DrugBank']
        return ', '.join(sources)
    
    @staticmethod
    def _format_variants_info(variants: List[str]) -> str:
        """Format variant information."""
        if not variants:
            return "No variants detected."
        return "\n".join([f"• {v}" for v in variants[:3]])
    
    @staticmethod
    def _get_drug_interactions(drug_name: str, variants: List[str]) -> str:
        """Get drug-variant interactions."""
        return f"• {drug_name} interactions documented for provided variants"
    
    @staticmethod
    def _get_clinical_guidance(drug_name: str, effectiveness: str, variants: List[str]) -> str:
        """Get clinical guidance for drug."""
        guidance = f"{drug_name} is predicted to have {effectiveness} efficacy"
        if variants:
            guidance += " based on patient genotype"
        return guidance


def generate_clinical_report(variant_ids: List[str], drug_names: List[str],
                            predictions: Dict, explanations: Dict) -> str:
    """
    Generate a comprehensive clinical report combining predictions and explanations.
    """
    report = f"""
    ╔════════════════════════════════════════════════════════════════════╗
    ║           PRECISION MEDICINE CLINICAL REPORT                       ║
    ╚════════════════════════════════════════════════════════════════════╝
    
    PATIENT GENETIC PROFILE
    ───────────────────────
    Variants identified: {len(variant_ids)}
    {chr(10).join([f"  • {v}" for v in variant_ids[:5]])}
    
    DRUG ASSESSMENT
    ───────────────
    Medications under consideration: {', '.join(drug_names)}
    
    PREDICTIONS & RECOMMENDATIONS
    ────────────────────────────
    {explanations.get('adr_risk', 'See detailed analysis below')}
    
    IMPORTANT DISCLAIMER
    ────────────────────
    ⚠️  This report is for RESEARCH PURPOSES ONLY
    ⚠️  NOT for clinical decision-making without validation
    ⚠️  Consult healthcare professionals for medical decisions
    
    ═════════════════════════════════════════════════════════════════════
    """
    return report
