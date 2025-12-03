# 🧬 Precision Pharma AI Platform - Implementation Guide

## 📋 Project Overview

This is a **flagship precision medicine AI platform** that predicts gene-drug responses and adverse drug reactions. It showcases enterprise-grade AI/ML engineering with genomics domain expertise.

**Perfect for:**
- Healthcare AI roles
- Pharma analytics positions
- Clinical decision support systems
- Biotech company AI teams
- AI/ML interviewing

---

## 🏗️ Architecture Overview

```
User/Demo UI (Streamlit)
         ↓
    FastAPI (REST)
         ↓
  ┌─────────────────────────────────────────┐
  │  Model Service                          │
  │  - XGBoost (ADR, Drug Response)         │
  │  - CNN/Transformer (Optional)           │
  │  - SHAP Explainability                  │
  └─────────────────────────────────────────┘
         ↓
  ┌─────────────────────────────────────────┐
  │  Data Pipeline                          │
  │  - VCF Parser (pysam)                   │
  │  - Variant Annotator                    │
  │  - Feature Engineering                  │
  └─────────────────────────────────────────┘
         ↓
  ┌─────────────────────────────────────────┐
  │  Data Layer                             │
  │  - Neo4j KG (Gene-Drug-Disease)         │
  │  - Vector DB (FAISS/Chroma)             │
  │  - PostgreSQL (Optional)                │
  └─────────────────────────────────────────┘
```

---

## 🚀 Getting Started (5 Minutes)

### 1. Install Dependencies
```bash
cd /Users/shaluu/learn/precision-pharma
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Run Setup Script
```bash
python setup.py
```

### 4. Start Development

**Option A: Using Docker (Recommended)**
```bash
docker-compose up
# Access: 
#   - API: http://localhost:8000/docs
#   - Dashboard: http://localhost:8501
#   - Neo4j: http://localhost:7474
```

**Option B: Local Development**

Terminal 1 - API:
```bash
uvicorn src.api.main:app --reload --port 8000
```

Terminal 2 - Dashboard:
```bash
streamlit run src/ui/app.py
```

### 5. Explore
- API Docs: http://localhost:8000/docs
- Streamlit UI: http://localhost:8501
- Demo Notebook: `notebooks/end_to_end_demo.ipynb`

---

## 📁 Project Structure

```
precision-pharma/
├── data/                          # Genomic datasets
│   ├── raw/                       # Raw VCF files, databases
│   └── processed/                 # Clean datasets, features
│
├── src/                           # Main application code
│   ├── pipeline/                  # Variant annotation
│   │   ├── vcf_parser.py         # VCF parsing & annotation
│   │   └── __init__.py
│   │
│   ├── models/                    # Predictive models
│   │   ├── predictors.py         # XGBoost, LightGBM models
│   │   └── __init__.py
│   │
│   ├── kg/                        # Knowledge graph
│   │   ├── knowledge_graph.py    # Neo4j integration
│   │   └── __init__.py
│   │
│   ├── api/                       # FastAPI service
│   │   ├── main.py               # REST endpoints
│   │   └── __init__.py
│   │
│   ├── ui/                        # Streamlit dashboard
│   │   ├── app.py                # Interactive UI
│   │   └── __init__.py
│   │
│   └── explainability/            # Explainable AI
│       ├── shap_explainer.py     # SHAP, LLM explanations
│       └── __init__.py
│
├── notebooks/                     # Jupyter notebooks
│   ├── end_to_end_demo.ipynb     # Full pipeline demo
│   ├── model_training.ipynb      # Model training guide
│   ├── rag_evaluation.ipynb      # RAG system evaluation
│   └── kg_construction.ipynb     # Knowledge graph build
│
├── tests/                         # Unit tests
│   ├── test_core.py              # Core functionality tests
│   └── conftest.py               # Test fixtures
│
├── .vscode/                       # VS Code configuration
│   ├── tasks.json                # Custom tasks
│   └── settings.json             # Workspace settings
│
├── requirements.txt              # Python dependencies
├── setup.py                      # Package setup
├── Dockerfile                    # Docker image
├── docker-compose.yml           # Multi-container setup
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
└── README.md                    # Full documentation
```

---

## 🔑 Core Modules Explained

### 1. **VCF Parser** (`src/pipeline/vcf_parser.py`)
- **Purpose**: Parse genetic variant files
- **Key Classes**:
  - `Variant`: Data class for genetic variants
  - `VCFParser`: Parse VCF files with pysam
  - `VariantAnnotator`: Add genomic annotations
- **Usage**:
  ```python
  parser = VCFParser("file.vcf")
  variants = parser.parse()
  annotator = VariantAnnotator()
  annotated = annotator.annotate_variants(variants)
  ```

### 2. **Predictive Models** (`src/models/predictors.py`)
- **Purpose**: ML models for risk/response prediction
- **Models**:
  - `ADRRiskPredictor`: Adverse drug reaction risk (0-1)
  - `DrugResponsePredictor`: Drug effectiveness (0-1)
  - `PathogenicityClassifier`: Variant severity (4-class)
- **Features**:
  - Training with sklearn/xgboost
  - SHAP-compatible for explainability
  - Cross-validation support
- **Usage**:
  ```python
  model = ADRRiskPredictor(model_type='xgboost')
  model.train(X_train, y_train)
  predictions = model.predict(X_test)
  importance = model.get_feature_importance(top_k=10)
  ```

### 3. **Knowledge Graph** (`src/kg/knowledge_graph.py`)
- **Purpose**: Neo4j-based pharmacogenomics database
- **Nodes**: Gene, Variant, Drug, Disease, Study
- **Relationships**: HAS_VARIANT, AFFECTS, TREATS
- **Queries**:
  - Find variants for a gene
  - Find drugs affected by variants
  - Find gene-drug interactions
  - Get drug indications
- **Usage**:
  ```python
  kg = KnowledgeGraphManager(uri, user, password)
  variants = kg.find_variants_for_gene('CYP2C19')
  interactions = kg.find_gene_drug_interactions('CYP2C19', 'warfarin')
  ```

### 4. **Explainability** (`src/explainability/shap_explainer.py`)
- **Purpose**: Make predictions interpretable
- **Features**:
  - SHAP force plots
  - Feature importance
  - Counterfactual explanations
  - LLM-generated natural language explanations
- **Usage**:
  ```python
  explainer = ModelExplainer(model, X_data)
  explanation = explainer.explain_prediction(sample_idx, X_test)
  llm = LLMExplainer()
  text = llm.explain_adr_risk(variants, drugs, probability)
  ```

### 5. **FastAPI Service** (`src/api/main.py`)
- **Purpose**: REST API for model inference
- **Endpoints**:
  - `POST /variants/annotate` - Annotate variants
  - `POST /vcf/upload` - Parse VCF file
  - `POST /predict/adr` - Predict ADR risk
  - `POST /predict/drug_response` - Predict effectiveness
  - `GET /kg/*` - Query knowledge graph
  - `GET /explain/*` - Get explanations
- **Example**:
  ```bash
  curl -X POST http://localhost:8000/predict/adr \
    -H "Content-Type: application/json" \
    -d '{"variants": ["chr10:94761930:G>A"], "drugs": ["warfarin"]}'
  ```

### 6. **Streamlit Dashboard** (`src/ui/app.py`)
- **Purpose**: Interactive web UI for all features
- **Pages**:
  - 🏠 Home - Overview & quick start
  - 📤 Upload VCF - File upload & parsing
  - 🔍 Variant Explorer - Browse & filter variants
  - 💊 Drug Response - Predict risk & effectiveness
  - 📊 Knowledge Graph - Query relationships
  - ⚙️ Settings - Configuration & help
- **Features**:
  - Real-time predictions
  - Interactive visualizations (Plotly)
  - SHAP explanations
  - Report generation
  - Risk gauges & heatmaps

---

## 📊 Data Sources

| Source | Type | Use Case |
|--------|------|----------|
| **PharmGKB** | Gene-drug annotations | Interactions, dosing guidelines |
| **ClinVar** | Variant classification | Pathogenicity labels |
| **DrugBank** | Drug database | Properties, targets, interactions |
| **gnomAD** | Population frequencies | Allele frequency background |
| **ENCODE** | Gene expression | Expression predictions (optional) |
| **PubMed** | Literature | Evidence for KG, RAG retrieval |

---

## 🔬 Running the Demo

### Jupyter Notebook
```bash
# Navigate to notebooks/
jupyter notebook end_to_end_demo.ipynb

# Or run with nbconvert
jupyter nbconvert --to notebook --execute end_to_end_demo.ipynb
```

The notebook demonstrates:
1. ✓ Variant annotation
2. ✓ Feature matrix creation
3. ✓ Model training (XGBoost)
4. ✓ Risk predictions
5. ✓ SHAP explanations
6. ✓ LLM natural language explanations
7. ✓ Model evaluation (ROC curves)
8. ✓ Clinical report generation

### Run Tests
```bash
# All tests
pytest tests/ -v

# With coverage report
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html  # View coverage

# Specific test
pytest tests/test_core.py::TestModelTraining::test_adr_model_training -v
```

---

## 🎯 Key Features to Demonstrate

### 1. **Variant Annotation**
- Parse VCF files
- Add CADD scores, conservation
- ClinVar significance
- Gene mapping

### 2. **Predictive Modeling**
- XGBoost for interpretability
- Feature importance
- Cross-validation
- Probability calibration

### 3. **Explainability**
- SHAP force plots
- Per-sample feature contributions
- Counterfactual analysis
- Clinical explanations

### 4. **Knowledge Graph**
- Neo4j integration
- Cypher queries
- Gene-drug relationships
- Evidence tracking

### 5. **RAG Integration**
- Vector embeddings
- Retrieval of evidence
- LLM-generated explanations
- Citations & references

### 6. **User Interface**
- Streamlit dashboard
- File uploads
- Interactive visualizations
- Report generation

---

## 🔐 Privacy & Ethics Checklist

- ✅ Use only public/synthetic data for demo
- ✅ De-identify any patient information
- ✅ Encrypt sensitive data
- ✅ Clear disclaimer: NOT for clinical use
- ✅ Document data sources & lineage
- ✅ Follow GDPR, HIPAA guidance
- ✅ Version all datasets (DVC)

---

## 🚢 Deployment Options

### Local Development
```bash
# Terminal 1
uvicorn src.api.main:app --reload

# Terminal 2
streamlit run src/ui/app.py
```

### Docker Container
```bash
docker build -t precision-pharma:latest .
docker run -p 8000:8000 -p 8501:8501 precision-pharma:latest
```

### Docker Compose (Recommended)
```bash
docker-compose up -d
# Services: API (8000), UI (8501), Neo4j (7687, 7474)
```

### Cloud Deployment
- **API**: AWS ECS, GCP Cloud Run, Heroku
- **UI**: Streamlit Cloud, Hugging Face Spaces
- **DB**: Neo4j AuraDB, managed PostgreSQL
- **Vector DB**: Chroma, FAISS on cloud instance

---

## 📈 Expected Performance Metrics

### ADR Risk Model
- **AUC-ROC**: 0.85 (5-fold CV)
- **AUC-PR**: 0.78
- **Specificity**: 0.92 @ 90% sensitivity
- **Calibration**: Brier score < 0.2

### Pathogenicity Classifier
- **Accuracy**: 91% (ClinVar test)
- **F1 (Pathogenic)**: 0.87
- **Sensitivity**: 0.89
- **Specificity**: 0.93

---

## 🧪 Testing Strategy

### Unit Tests (`tests/test_core.py`)
- ✓ Variant annotation
- ✓ Model training & prediction
- ✓ Feature importance
- ✓ SHAP explainability
- ✓ Knowledge graph operations

### Integration Tests
- ✓ Full pipeline (VCF → prediction)
- ✓ API endpoint testing
- ✓ KG queries
- ✓ UI functionality

### Validation
- ✓ Cross-validation
- ✓ Held-out test set
- ✓ Subgroup analysis
- ✓ Error analysis

---

## 🎓 Learning Resources

### Genomics
- [PharmGKB Documentation](https://www.pharmgkb.org/)
- [ClinVar Interpretation](https://www.ncbi.nlm.nih.gov/clinvar/)
- [VCF Format Specification](https://samtools.github.io/hts-specs/)

### ML/AI
- [SHAP Documentation](https://shap.readthedocs.io/)
- [XGBoost Guide](https://xgboost.readthedocs.io/)
- [Feature Engineering Handbook](https://feature-engine.readthedocs.io/)

### Knowledge Graphs
- [Neo4j Graph Academy](https://graphacademy.neo4j.com/)
- [Cypher Query Language](https://neo4j.com/docs/cypher-manual/)

### Web Frameworks
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Streamlit Docs](https://docs.streamlit.io/)

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Code Standards
- Follow PEP 8
- Use type hints
- Write docstrings
- Include unit tests
- Update README

---

## 📞 Support & Help

- **Issues**: Create GitHub issue
- **Documentation**: See README.md
- **API Docs**: http://localhost:8000/docs
- **Notebooks**: `notebooks/` folder
- **Code Comments**: Inline documentation

---

## ⚠️ Important Disclaimer

```
THIS PLATFORM IS FOR RESEARCH PURPOSES ONLY.

NOT for clinical decision-making without:
- Proper validation & testing
- Regulatory approval (FDA, EMA, etc.)
- Clinical review & oversight
- Patient consent & privacy compliance

Always consult healthcare professionals.
Follow all applicable privacy & security regulations.
```

---

## 📜 License

MIT License - See LICENSE file

---

## 🙏 Acknowledgments

- PharmGKB, ClinVar, DrugBank for open data
- XGBoost, SHAP, Neo4j open source projects
- Streamlit & FastAPI communities

---

**Built with ❤️ for precision medicine and healthcare AI**

Last Updated: December 2, 2024
