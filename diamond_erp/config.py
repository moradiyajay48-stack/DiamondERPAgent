"""
Diamond ERP Configuration
Shared constants and configuration for the multi-agent ERP system.
"""

import os
from pathlib import Path

# --- Paths ---
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "diamond_erp.db"

# --- Model ---
DEFAULT_MODEL = "gemini-2.0-flash"

# --- Diamond Industry Constants ---
DIAMOND_SHAPES = [
    "Round Brilliant", "Princess", "Cushion", "Oval", "Emerald",
    "Pear", "Marquise", "Asscher", "Radiant", "Heart"
]

COLOR_GRADES = ["D", "E", "F", "G", "H", "I", "J", "K", "L", "M"]
CLARITY_GRADES = ["FL", "IF", "VVS1", "VVS2", "VS1", "VS2", "SI1", "SI2", "I1", "I2", "I3"]
CUT_GRADES = ["Excellent", "Very Good", "Good", "Fair", "Poor"]
FLUORESCENCE_GRADES = ["None", "Faint", "Medium", "Strong", "Very Strong"]

STONE_STATUSES = ["available", "planned", "in_process", "polished", "graded", "certified", "sold"]
PROCESS_TYPES = ["sawing", "bruting", "cutting", "polishing"]

LABS = ["GIA", "IGI", "HRD", "AGS"]

# --- Estimated Yield Percentages by Shape ---
YIELD_ESTIMATES = {
    "Round Brilliant": 0.42,
    "Princess": 0.50,
    "Cushion": 0.48,
    "Oval": 0.52,
    "Emerald": 0.55,
    "Pear": 0.45,
    "Marquise": 0.44,
    "Asscher": 0.50,
    "Radiant": 0.48,
    "Heart": 0.40,
}
