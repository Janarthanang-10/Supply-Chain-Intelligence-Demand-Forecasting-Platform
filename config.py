"""
config.py
---------
Central configuration for the Supply Chain Analytics Dashboard.
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_PATH = os.path.join(DATA_DIR, "supply_chain_data.csv")
MODEL_DIR = os.path.join(BASE_DIR, "model")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
STYLE_CSS_PATH = os.path.join(ASSETS_DIR, "style.css")

APP_TITLE = "Supply Chain Analytics Dashboard"
APP_ICON = "📦"

PRIMARY_COLOR = "#2E86AB"
SUCCESS_COLOR = "#06A77D"
WARNING_COLOR = "#F4A259"
DANGER_COLOR = "#E63946"
