"""Streamlit app package that wraps the existing UI code under `src.ui`.
This package provides a forward-compatible structure for pages/components.
"""

from typing import Any

try:
    # Attempt to reuse the existing Streamlit app if present
    from src.ui.app import main as run_app
except Exception:
    run_app = None

__all__ = ["run_app"]