"""
Configuration constants for Precision Pharma AI Platform.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project Root
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Data Directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Models
MODELS_DIR = PROJECT_ROOT / "models"

# External API Configuration
# External API Configuration
CLINVAR_API_URL = os.getenv("CLINVAR_API_URL", "https://eutils.ncbi.nlm.nih.gov/entrez/eutils")
GNOMAD_API_URL = os.getenv("GNOMAD_API_URL", "https://gnomad.broadinstitute.org/api")
OPENFDA_EVENT_URL = os.getenv("OPENFDA_EVENT_URL", "https://api.fda.gov/drug/event.json")
OPENFDA_LABEL_URL = os.getenv("OPENFDA_LABEL_URL", "https://api.fda.gov/drug/label.json")
MYGENE_URL = os.getenv("MYGENE_URL", "https://mygene.info/v3/query")
DGIDB_URL = os.getenv("DGIDB_URL", "https://dgidb.org/api/graphql")
PUBCHEM_URL = os.getenv("PUBCHEM_URL", "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name")

# Fallback/Mock Data (Minimal set for testing/offline mode)
MOCK_CLINVAR_FALLBACK = {
    'chr10:94761930:G>A': {'significance': 'pathogenic', 'id': 'VCV000000001'},
    'chr6:161006172:G>A': {'significance': 'likely_pathogenic', 'id': 'VCV000000002'},
    'chr19:41307769:C>T': {'significance': 'benign', 'id': 'VCV000000003'},
}

DRUG_METABOLIZER_GENES = {
    'CYP2C19': {'cyp_family': 'CYP2C19', 'drugs': ['clopidogrel', 'omeprazole', 'escitalopram']},
    'CYP2C9': {'cyp_family': 'CYP2C9', 'drugs': ['warfarin', 'nsaid']},
    'CYP2D6': {'cyp_family': 'CYP2D6', 'drugs': ['codeine', 'tramadol', 'metoprolol']},
    'CYP3A4': {'cyp_family': 'CYP3A4', 'drugs': ['simvastatin', 'atorvastatin']},
    'TPMT': {'cyp_family': 'TPMT', 'drugs': ['azathioprine', '6-mercaptopurine']},
    'VKORC1': {'cyp_family': 'VKORC1', 'drugs': ['warfarin']},
}
