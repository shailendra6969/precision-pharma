# Precision Pharma AI Platform 🔬💊

A comprehensive AI system for personalized medicine that predicts drug response and adverse reactions based on patient genetics, powered by explainable AI and knowledge graphs.

## 🎯 Overview

This flagship project combines **genomics + AI + NLP + knowledge graphs** to build a production-ready platform that:

- **Predicts gene-drug responses** using patient genetic variants (VCF files)
- **Assesses adverse drug reaction (ADR) risk** from genotype + clinical context
- **Classifies pathogenic variants** with high confidence
- **Powers a pharmacogenomics knowledge graph** (Neo4j) with gene-drug-disease relationships
- **Provides explainable AI insights** via SHAP and LLM-generated natural language explanations
- **Delivers results through an interactive Streamlit dashboard** with exportable reports

## 🏗️ Architecture

```
precision-pharma/
├─ data/                          # Raw & processed datasets
│  ├─ raw/                        # VCF files, raw databases
│  └─ processed/                  # Cleaned features, embeddings
├─ src/
│  ├─ pipeline/                   # VCF parsing, variant annotation
│  ├─ models/                     # XGBoost, CNN, Transformer models
│  ├─ kg/                         # Neo4j ingestion & Cypher queries
│  ├─ api/                        # FastAPI service
│  ├─ ui/                         # Streamlit dashboard
│  └─ explainability/             # SHAP, LLM explanations, RAG
├─ notebooks/                     # Exploratory notebooks
├─ tests/                         # Unit tests
├─ requirements.txt
└─ README.md
```

## 🚀 Core Components

### 1. **Variant Annotation Pipeline** (`src/pipeline/`)
- Parse VCF files with pysam
- Annotate variants with: gene, effect type, conservation scores, CADD, allele frequency
- Map to known drug-metabolizing genes (CYPs)
- Feature engineering for downstream models

### 2. **Predictive Models** (`src/models/`)
- **XGBoost/LightGBM**: Tabular drug response & ADR risk (interpretable, fast)
- **Multimodal CNN+Dense**: Sequence + clinical features
- **Pathogenicity Classifier**: Benign/Likely Benign/Pathogenic/Likely Pathogenic
- All models include SHAP explainability

### 3. **Pharmacogenomics Knowledge Graph** (`src/kg/`)
- **Neo4j database** connecting: Gene → Variant → Drug → Disease → Study
- Ingests PharmGKB, DrugBank, ClinVar data
- Supports graph queries: "Which CYP2C19 variants affect Warfarin?"
- Powers RAG evidence retrieval

### 4. **RAG + LLM Explanations** (`src/explainability/`)
- Vector DB (FAISS/Chroma) with curated pharmacogenomics passages
- Retrieval-augmented generation for context-aware explanations
- LLM-generated clinical recommendations with citations
- Counterfactual explanations

### 5. **FastAPI Service** (`src/api/`)
- Inference endpoints for: variant scoring, drug response prediction, ADR risk
- KG query endpoints
- Model serving with batch support
- Monitoring & logging with MLflow

### 6. **Streamlit Dashboard** (`src/ui/`)
- **Upload VCF** or paste variant list
- **Summary dashboard**: per-drug risk (green/yellow/red)
- **Variant explorer**: detailed annotations, conservation, frequencies
- **Knowledge graph explorer**: interactive network visualization
- **Explainability tab**: SHAP plots + LLM explanations with citations
- **Export**: PDF report with recommendations

## 📊 Data Sources

| Source | Type | Purpose |
|--------|------|---------|
| **PharmGKB** | Gene-drug annotations | Drug-variant interactions, dosing |
| **ClinVar** | Variant pathogenicity | Classification labels, evidence |
| **DrugBank** | Drug database | Drug structures, targets, interactions |
| **1000 Genomes / gnomAD** | Population genetics | Allele frequencies, background |
| **ENCODE / GEO** | Gene expression | Expression predictions (optional) |
| **PubMed / PMC** | Literature | Evidence for KG, RAG retrieval |

## 🔧 Installation & Setup

### Prerequisites
- Python 3.10+
- Neo4j instance (AuraDB or local)
- Optional: GPU (NVIDIA) for transformer models

### Setup
```bash
# Clone the repo
git clone <repo-url>
cd precision-pharma

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with Neo4j credentials, OpenAI key, etc.

# Initialize databases
python src/kg/ingest_pharmgkb.py
python src/pipeline/build_annotation_tables.py
```

### Run Streamlit App
```bash
streamlit run src/ui/app.py
```

### Start API Service
```bash
uvicorn src.api.main:app --reload --port 8000
```

## 📈 Model Performance

### ADR Risk Prediction (XGBoost)
- **AUC-ROC**: 0.85 (5-fold CV)
- **AUC-PR**: 0.78
- **Specificity**: 0.92 @ 90% sensitivity

### Pathogenicity Classification (CNN)
- **Accuracy**: 91% on ClinVar test set
- **F1 (Pathogenic)**: 0.87

*See `notebooks/model_evaluation.ipynb` for detailed metrics & calibration analysis.*

## 🧠 Key Features

### Explainability
- **SHAP force plots**: Per-sample feature contributions
- **SHAP summary plots**: Global feature importance
- **Counterfactual analysis**: "If variant X were absent, risk would be Y"
- **LLM explanations**: Natural language reasoning with evidence links

### Knowledge Graph Queries (Cypher Examples)
```cypher
# Which CYP2C9 variants affect Warfarin dosing?
MATCH (g:Gene {symbol:"CYP2C9"})-[:HAS_VARIANT]->(v:Variant)
       -[r:AFFECTS]->(d:Drug {name:"Warfarin"})
RETURN v.id, r.effect_type, r.study_count ORDER BY r.study_count DESC

# Gene-drug interactions for a given variant
MATCH (v:Variant {id:"chr10:94761930:G>A"})-[:AFFECTS]->(d:Drug)
RETURN d.name, d.effect_type, count(d) as num_interactions
```

### API Examples
```bash
# Predict ADR risk
curl -X POST http://localhost:8000/predict/adr \
  -H "Content-Type: application/json" \
  -d '{
    "variants": ["chr10:94761930:G>A", "chr22:42127942:C>T"],
    "drugs": ["warfarin", "omeprazole"],
    "age": 65, "renal_function": "normal"
  }'

# Explain prediction
curl -X GET http://localhost:8000/explain/adr?variant_id=chr10:94761930:G>A

# Query knowledge graph
curl -X GET "http://localhost:8000/kg/query?gene=CYP2C19&drug=warfarin"
```

## 🧪 Testing

```bash
# Run unit tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## 📚 Notebooks

- **`EDA_variants.ipynb`**: Exploratory data analysis of variant datasets
- **`model_training.ipynb`**: XGBoost & CNN model training pipeline
- **`kg_construction.ipynb`**: Knowledge graph build & Cypher examples
- **`rag_evaluation.ipynb`**: RAG retrieval quality & LLM explanations
- **`end_to_end_demo.ipynb`**: Full pipeline from VCF → prediction → explanation

## 🔐 Privacy & Ethics

- ✅ All patient data de-identified (demo uses synthetic/public data)
- ✅ Encrypted storage for any PHI (encryption at rest & transit)
- ✅ Clear disclaimer: **NOT for clinical use without validation & certification**
- ✅ Data provenance & versioning tracked (DVC)
- ✅ Follows GDPR, HIPAA guidance (where applicable)

## 🚢 Deployment

### Docker
```bash
docker build -t precision-pharma:latest .
docker run -p 8000:8000 -p 8501:8501 precision-pharma:latest
```

### Cloud Options
- **FastAPI + Uvicorn**: AWS ECS / GCP Cloud Run / Heroku
- **Streamlit**: Streamlit Cloud or Hugging Face Spaces
- **Neo4j**: AuraDB (managed) or self-hosted
- **Vector DB**: Chroma (embedded) or FAISS (on-prem)
- **LLM**: OpenAI API or self-hosted Llama-2 / Mistral on GPU

## 🎓 Learning Resources

- [PharmGKB Documentation](https://www.pharmgkb.org/)
- [ClinVar Variant Classification](https://www.ncbi.nlm.nih.gov/clinvar/)
- [Neo4j Graph Academy](https://graphacademy.neo4j.com/)
- [SHAP Documentation](https://shap.readthedocs.io/)
- [Streamlit Docs](https://docs.streamlit.io/)

## 🤝 Contributing

Contributions welcome! Please follow PEP 8 and include tests for new features.

## 📄 License

MIT

---

**Built for:** Healthcare AI, Precision Medicine, Pharma Analytics, Clinical Decision Support  
**AI Skills Showcased:** NLP, XGBoost/LightGBM, CNN, LSTM, Knowledge Graphs, RAG, Explainable AI, Streamlit
