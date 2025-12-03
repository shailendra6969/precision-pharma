""""""




























































)    },        ],            "sphinx-rtd-theme>=1.0.0",            "sphinx>=5.0.0",        "docs": [        ],            "mypy>=1.0.0",            "flake8>=6.0.0",            "black>=23.0.0",            "pytest-cov>=4.1.0",            "pytest>=7.4.0",        "dev": [    extras_require={    ],        "langchain>=0.1.0",        "neo4j>=5.14.0",        "shap>=0.43.0",        "streamlit>=1.31.0",        "uvicorn>=0.27.0",        "fastapi>=0.109.0",        "transformers>=4.35.0",        "torch>=2.1.0",        "lightgbm>=4.1.0",        "xgboost>=2.0.0",        "scikit-learn>=1.3.0",        "numpy>=1.24.0",        "pandas>=2.1.0",    install_requires=[    python_requires=">=3.10",    ],        "Topic :: Scientific/Engineering :: Medical Science Apps.",        "Topic :: Scientific/Engineering :: Bio-Informatics",        "Intended Audience :: Science/Research",        "Development Status :: 3 - Alpha",        "Operating System :: OS Independent",        "License :: OSI Approved :: MIT License",        "Programming Language :: Python :: 3.10",        "Programming Language :: Python :: 3",    classifiers=[    packages=find_packages(),    url="https://github.com/yourusername/precision-pharma",    long_description_content_type="text/markdown",    long_description=long_description,    description="Gene-drug response prediction platform with explainable AI",    author_email="your.email@example.com",    author="Your Name",    version="0.1.0",    name="precision-pharma",setup(    long_description = fh.read()with open("README.md", "r", encoding="utf-8") as fh:from setuptools import setup, find_packages"""Packaging and installation configurationPrecision Pharma AI PlatformSetup script to initialize the Precision Pharma AI Platform
"""

import os
import sys
from pathlib import Path
import shutil
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def setup_directories():
    """Create necessary project directories."""
    logger.info("📁 Setting up directories...")
    
    dirs = [
        'data/raw',
        'data/processed',
        'models',
        'logs',
        'outputs/reports',
        'outputs/visualizations',
    ]
    
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
        logger.info(f"  ✓ {d}")


def setup_environment():
    """Setup environment variables."""
    logger.info("\n🔐 Setting up environment...")
    
    env_file = '.env'
    env_example = '.env.example'
    
    if not Path(env_file).exists() and Path(env_example).exists():
        shutil.copy(env_example, env_file)
        logger.info(f"  ✓ Created {env_file} from template")
        logger.info("  ⚠️  Edit .env with your API keys and database credentials")
    else:
        logger.info(f"  ✓ {env_file} already exists")


def install_dependencies():
    """Install required Python packages."""
    logger.info("\n📦 Installing dependencies...")
    
    # Check if pip is available
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            logger.info("  ✓ Dependencies installed successfully")
        else:
            logger.error(f"  ✗ Error installing dependencies: {result.stderr}")
    except Exception as e:
        logger.error(f"  ✗ Error: {e}")


def verify_imports():
    """Verify that key modules can be imported."""
    logger.info("\n✅ Verifying imports...")
    
    modules_to_check = [
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('torch', 'PyTorch'),
        ('sklearn', 'scikit-learn'),
        ('xgboost', 'XGBoost'),
        ('lightgbm', 'LightGBM'),
        ('fastapi', 'FastAPI'),
        ('streamlit', 'Streamlit'),
        ('neo4j', 'Neo4j driver'),
        ('shap', 'SHAP'),
    ]
    
    success_count = 0
    for module, name in modules_to_check:
        try:
            __import__(module)
            logger.info(f"  ✓ {name}")
            success_count += 1
        except ImportError:
            logger.warning(f"  ✗ {name} - Not installed (optional)")
    
    logger.info(f"\n  {success_count}/{len(modules_to_check)} core packages verified")


def create_data_placeholder():
    """Create placeholder files for data directories."""
    logger.info("\n📊 Creating data placeholders...")
    
    # Create .gitkeep files
    for d in ['data/raw', 'data/processed']:
        gitkeep = Path(d) / '.gitkeep'
        gitkeep.touch()
    
    logger.info("  ✓ Data directories ready")


def print_next_steps():
    """Print next steps for user."""
    logger.info("""
╔═══════════════════════════════════════════════════════════════════╗
║          SETUP COMPLETE ✓                                        ║
╚═══════════════════════════════════════════════════════════════════╝

🚀 NEXT STEPS:

1. Configure Environment Variables:
   • Edit .env with your settings
   • Add Neo4j credentials if using local instance
   • Add OpenAI API key for LLM features

2. Start Development:
   
   Option A - Using Docker:
   $ docker-compose up
   
   Option B - Local Development:
   
   Terminal 1 (API):
   $ uvicorn src.api.main:app --reload
   
   Terminal 2 (UI):
   $ streamlit run src/ui/app.py
   
   Terminal 3 (Neo4j - if running locally):
   $ neo4j start

3. Access Services:
   • API Docs: http://localhost:8000/docs
   • Dashboard: http://localhost:8501
   • Neo4j Browser: http://localhost:7474

4. Run Demo:
   • Open notebooks/end_to_end_demo.ipynb in Jupyter
   • Run cells to see the complete pipeline

5. Run Tests:
   $ pytest tests/ -v
   $ pytest tests/ --cov=src --cov-report=html

📚 DOCUMENTATION:
   • README.md - Full documentation
   • docs/ - API documentation
   • notebooks/ - Examples and tutorials

❓ HELP:
   • Check GitHub Issues
   • Review inline code comments
   • See CONTRIBUTING.md for development guidelines

⚠️  IMPORTANT:
   • This is for RESEARCH ONLY
   • NOT for clinical decision-making without validation
   • Follow privacy and security best practices
   • De-identify any real patient data

Happy coding! 🧬
    """)


if __name__ == '__main__':
    logger.info("""
╔═══════════════════════════════════════════════════════════════════╗
║   Precision Pharma AI Platform - Setup Script                    ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        setup_directories()
        setup_environment()
        create_data_placeholder()
        verify_imports()
        print_next_steps()
        
        logger.info("\n✓ Setup completed successfully!")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n✗ Setup failed: {e}")
        sys.exit(1)
