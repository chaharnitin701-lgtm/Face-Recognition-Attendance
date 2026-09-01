"""
config.py
---------
Central configuration file for folder paths and app settings.
All paths are created automatically on startup if they don't exist.
"""

import os

# ── Base directory (attendance_system/) ───────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── Sub-directories ────────────────────────────────────────────────────────────
DATASET_DIR   = os.path.join(BASE_DIR, "dataset")       # raw captured face images
ENCODINGS_DIR = os.path.join(BASE_DIR, "encodings")     # saved face encoding files
ATTENDANCE_DIR = os.path.join(BASE_DIR, "attendance")   # attendance CSV files

# ── Files ──────────────────────────────────────────────────────────────────────
ATTENDANCE_CSV  = os.path.join(ATTENDANCE_DIR, "attendance.csv")
ENCODINGS_FILE  = os.path.join(ENCODINGS_DIR, "encodings.pkl")

# ── Webcam settings ────────────────────────────────────────────────────────────
WEBCAM_INDEX       = 0          # change to 1 if external webcam is needed
CAPTURE_IMAGES     = 30         # number of images captured per student during registration
RECOGNITION_TOLERANCE = 0.5    # lower = stricter matching

# ── GUI colours (modern dark theme) ───────────────────────────────────────────
BG_COLOR       = "#1a1a2e"      # deep navy background
PANEL_COLOR    = "#16213e"      # slightly lighter panel
ACCENT_COLOR   = "#0f3460"      # accent blue
BTN_COLOR      = "#e94560"      # vibrant red-pink button
BTN_HOVER      = "#c73652"
BTN_TEXT       = "#ffffff"
TITLE_COLOR    = "#e94560"
TEXT_COLOR     = "#eaeaea"
SUCCESS_COLOR  = "#00d4aa"
WARNING_COLOR  = "#ffd166"
TABLE_HEADER   = "#0f3460"
TABLE_ROW_ODD  = "#1a1a2e"
TABLE_ROW_EVEN = "#16213e"

# ── Font settings ──────────────────────────────────────────────────────────────
FONT_TITLE  = ("Helvetica", 22, "bold")
FONT_LABEL  = ("Helvetica", 12)
FONT_BOLD   = ("Helvetica", 12, "bold")
FONT_SMALL  = ("Helvetica", 10)
FONT_BTN    = ("Helvetica", 12, "bold")

def ensure_directories():
    """Create all required project directories if they do not exist."""
    for directory in [DATASET_DIR, ENCODINGS_DIR, ATTENDANCE_DIR]:
        os.makedirs(directory, exist_ok=True)
