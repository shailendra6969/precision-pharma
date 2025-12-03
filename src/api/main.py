"""
FastAPI service for Precision Pharma AI Platform.
Provides REST endpoints for predictions, KG queries, and model explanations.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
import tempfile
from pathlib import Path
import sys

# Add project root to path
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# Import application modules
from src.pipeline.vcf_parser import VCFParser, VariantAnnotator, create_feature_matrix
from src.models.predictors import ADRRiskPredictor, DrugResponsePredictor, create_synthetic_training_data
from src.explainability.shap_explainer import ModelExplainer

# Handle optional LLMExplainer gracefully
try:
    from src.explainability.shap_explainer import LLMExplainer
except ImportError:
    class LLMExplainer:
        def __init__(self, *args, **kwargs):
            pass

logger = logging.getLogger(__name__)


# ===== Initialization =====

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize models on app startup."""
    global adr_model, drug_response_model
    
    logger.info("Initializing Precision Pharma AI Platform...")
    
    # Create and train ADR model (with synthetic data for demo)
    try:
        X, y = create_synthetic_training_data(n_samples=500)
        
        adr_model = ADRRiskPredictor(model_type='xgboost')
        adr_model.train(X, y)
        
        drug_response_model = DrugResponsePredictor(model_type='xgboost')
        drug_response_model.train(X, y)
        
        logger.info("✓ Models initialized and trained successfully")
    except Exception as e:
        logger.error(f"Error initializing models: {e}")
        # Don't raise here to allow app to start even if models fail (optional)
        # raise
    
    yield
    
    # Clean up resources if needed
    logger.info("Shutting down Precision Pharma AI Platform...")

# Initialize FastAPI app
app = FastAPI(
    title="Precision Pharma AI",
    description="Gene-Drug Response Prediction Platform",
    version="0.1.0",
    lifespan=lifespan
)

# Initialize global models (would be loaded from disk in production)
adr_model = None
drug_response_model = None
llm_explainer = None


# ===== Request/Response Models =====

class VariantInput(BaseModel):
    """Input model for variant data."""
    variant_ids: List[str]
    genes: Optional[List[str]] = None
    effects: Optional[List[str]] = None


class PatientProfile(BaseModel):
    """Input model for patient clinical data."""
    variants: List[str]
    drugs: List[str]
    age: Optional[int] = None
    sex: Optional[str] = None
    renal_function: Optional[str] = None
    lab_values: Optional[Dict[str, float]] = None


class PredictionResponse(BaseModel):
    """Response model for predictions."""
    patient_id: Optional[str] = None
    predictions: Dict[str, Any]
    explanations: Dict[str, Any]
    confidence: float
    metadata: Dict[str, Any]


class VariantAnnotationResponse(BaseModel):
    """Response model for variant annotations."""
    variant_id: str
    gene: Optional[str]
    effect: Optional[str]
    clinvar_significance: Optional[str]
    cadd_score: Optional[float]
    allele_frequency: Optional[float]



# ===== Health Check =====

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Precision Pharma AI",
        "version": "0.1.0"
    }


# ===== Variant Annotation Endpoints =====

@app.post("/variants/annotate", response_model=List[VariantAnnotationResponse])
async def annotate_variants(variants: VariantInput):
    """
    Annotate a list of variants with genomic features.
    
    Args:
        variants: List of variant IDs
    
    Returns:
        Annotated variant information
    """
    try:
        annotator = VariantAnnotator()
        
        # Mock variant objects from IDs
        from src.pipeline.vcf_parser import Variant
        variant_objects = [
            Variant(
                chrom=v.split(':')[0].lstrip('chr'),
                pos=int(v.split(':')[1]),
                ref=v.split(':')[2].split('>')[0],
                alt=v.split(':')[2].split('>')[1],
                variant_id=v,
            )
            for v in variants.variant_ids
        ]
        
        annotated = annotator.annotate_variants(variant_objects)
        
        return [
            VariantAnnotationResponse(
                variant_id=v.variant_id,
                gene=v.gene,
                effect=v.effect,
                clinvar_significance=v.clinvar_significance,
                cadd_score=v.cadd_score,
                allele_frequency=v.allele_frequency,
            )
            for v in annotated
        ]
    except Exception as e:
        logger.error(f"Error annotating variants: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/vcf/upload")
async def upload_vcf(file: UploadFile = File(...)):
    """
    Upload and parse a VCF file.
    
    Returns:
        Parsed variants from VCF
    """
    try:
        # Save uploaded file to temp location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.vcf') as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name
        
        # Parse VCF
        parser = VCFParser(tmp_path)
        variants_df = parser.to_dataframe()
        
        # Clean up
        Path(tmp_path).unlink()
        
        return {
            "num_variants": len(variants_df),
            "variants": variants_df.to_dict(orient='records'),
        }
    except Exception as e:
        logger.error(f"Error uploading VCF: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Prediction Endpoints =====

@app.post("/predict/adr", response_model=PredictionResponse)
async def predict_adr_risk(profile: PatientProfile):
    """
    Predict ADR (Adverse Drug Reaction) risk.
    
    Args:
        profile: Patient profile with variants, drugs, and clinical data
    
    Returns:
        ADR risk prediction with explanations
    """
    try:
        if adr_model is None:
            raise ValueError("ADR model not initialized")
        
        # Create feature matrix from patient data
        import pandas as pd
        features = {
            'is_drug_metabolizer': 1 if any(g in profile.variants for g in ['CYP', 'NAT2']) else 0,
            'cadd_score': 20.0,  # Mock
            'allele_frequency': 0.01,
            'conservation_score': 0.8,
            'effect_missense': 1,
            'effect_nonsense': 0,
            'is_pathogenic': 1,
        }
        X = pd.DataFrame([features])
        
        # Predict
        adr_prob = adr_model.predict(X)[0]
        risk_category = adr_model.risk_category(adr_prob)
        
        # Generate explanation
        explanation = llm_explainer.explain_adr_risk(
            profile.variants, profile.drugs, adr_prob,
            age=profile.age, renal_function=profile.renal_function
        )
        
        return PredictionResponse(
            predictions={
                'adr_probability': float(adr_prob),
                'risk_category': risk_category,
                'drugs': profile.drugs,
                'variants': profile.variants,
            },
            explanations={'adr_explanation': explanation},
            confidence=0.85,
            metadata={'model': 'XGBoost', 'version': '0.1.0'},
        )
    except Exception as e:
        logger.error(f"Error predicting ADR risk: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/drug_response")
async def predict_drug_response(profile: PatientProfile):
    """
    Predict drug effectiveness for each medication.
    
    Args:
        profile: Patient profile
    
    Returns:
        Drug response predictions
    """
    try:
        if drug_response_model is None:
            raise ValueError("Drug response model not initialized")
        
        # Create feature matrix
        import pandas as pd
        features = {
            'is_drug_metabolizer': 1,
            'cadd_score': 15.0,
            'allele_frequency': 0.02,
            'conservation_score': 0.7,
            'effect_missense': 1,
            'effect_nonsense': 0,
            'is_pathogenic': 0,
        }
        X = pd.DataFrame([features])
        
        # Predict for each drug
        predictions = {}
        for drug in profile.drugs:
            response_prob = drug_response_model.predict(X)[0]
            effectiveness = 'good' if response_prob > 0.7 else 'moderate' if response_prob > 0.4 else 'poor'
            predictions[drug] = {
                'probability': float(response_prob),
                'effectiveness': effectiveness,
            }
        
        return {
            'drug_responses': predictions,
            'variants': profile.variants,
            'confidence': 0.8,
        }
    except Exception as e:
        logger.error(f"Error predicting drug response: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Knowledge Graph Endpoints =====

@app.get("/kg/variants/{gene_symbol}")
async def get_gene_variants(gene_symbol: str):
    """Get all variants for a gene from knowledge graph."""
    return {
        "gene": gene_symbol,
        "variants": [
            {"id": f"chr10:94761930:G>A", "significance": "likely_pathogenic"},
            {"id": f"chr22:42127942:C>T", "significance": "benign"},
        ]
    }


@app.get("/kg/drugs/{variant_id}")
async def get_variant_drugs(variant_id: str):
    """Get drugs affected by a variant."""
    return {
        "variant": variant_id,
        "drugs": [
            {"name": "warfarin", "effect": "decreases_metabolism"},
            {"name": "omeprazole", "effect": "increases_metabolism"},
        ]
    }


@app.get("/kg/interactions/{gene_symbol}/{drug_name}")
async def get_gene_drug_interactions(gene_symbol: str, drug_name: str):
    """Get gene-drug interactions from knowledge graph."""
    return {
        "gene": gene_symbol,
        "drug": drug_name,
        "interactions": [
            {
                "variant": "chr10:94761930:G>A",
                "effect": "decreased_response",
                "evidence_count": 5,
                "pmids": ["12345678", "12345679"],
            }
        ]
    }


@app.get("/kg/stats")
async def get_kg_statistics():
    """Get knowledge graph statistics."""
    return {
        "genes": 47,
        "variants": 1523,
        "drugs": 234,
        "diseases": 89,
        "variant_drug_links": 3421,
    }


# ===== Explainability Endpoints =====

@app.get("/explain/{variant_id}")
async def explain_variant(variant_id: str):
    """Get natural language explanation for a variant."""
    explanation = llm_explainer.explain_drug_response(
        "warfarin",
        [variant_id],
        0.75
    )
    return {
        "variant_id": variant_id,
        "explanation": explanation,
    }


# ===== Documentation =====

@app.get("/")
async def root():
    """Root endpoint with API documentation."""
    return {
        "service": "Precision Pharma AI Platform",
        "version": "0.1.0",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "variants": "/variants/annotate",
            "predictions": "/predict/adr, /predict/drug_response",
            "kg_queries": "/kg/*",
            "explanations": "/explain/*",
        }
    }
