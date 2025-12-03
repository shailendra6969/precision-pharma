from pathlib import Path

# UI Constants
APP_TITLE = "Precision Pharma AI Platform"
APP_ICON = "🔬"
VERSION = "1.0.0"
COPYRIGHT = "© 2024 Precision Pharma AI"

# Theme Colors (matching CSS)
COLOR_PRIMARY = "#2B6CB0"
COLOR_SECONDARY = "#2C5282"
COLOR_ACCENT = "#90CDF4"
COLOR_BACKGROUND = "#0F1117"
COLOR_TEXT = "#E2E8F0"

# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[3]
TEMP_DIR = Path("/tmp")
ASSETS_DIR = Path(__file__).parent.parent / "assets"

# Mock Data (if needed for UI-specific mocks)
DEMO_PATIENT_PROFILES = [
    {"id": "PT001", "age": 45, "sex": "Male", "renal": "Normal"},
    {"id": "PT002", "age": 62, "sex": "Female", "renal": "Impaired"},
]
