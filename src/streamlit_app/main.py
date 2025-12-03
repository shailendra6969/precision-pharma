import streamlit as st
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.streamlit_app.pages.home import render_home

# Entry point
if __name__ == "__main__":
    # In a standard Streamlit app with pages/, main.py is usually the "Home" or "Index".
    # We will reuse the Home page logic here.
    render_home()
