"""
database.py
-----------
Handles all attendance CSV read/write operations using Pandas.
Also manages the student registry (encodings pickle file).
"""

import os
import pickle
import pandas as pd
from datetime import datetime
from app.config import ATTENDANCE_CSV, ENCODINGS_FILE, ensure_directories

# ── CSV Column Names ───────────────────────────────────────────────────────────
COLUMNS = ["Student ID", "Student Name", "Date", "Time", "Status"]


def init_attendance_csv():
    """Create the attendance CSV with headers if it doesn't exist."""
    ensure_directories()
    if not os.path.exists(ATTENDANCE_CSV):
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(ATTENDANCE_CSV, index=False)


def load_attendance() -> pd.DataFrame:
    """Load attendance records from CSV. Returns empty DataFrame if file missing."""
    init_attendance_csv()
    try:
        df = pd.read_csv(ATTENDANCE_CSV)
        # Ensure all expected columns exist
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = ""
        return df
    except Exception as e:
        print(f"[DB] Error loading attendance: {e}")
        return pd.DataFrame(columns=COLUMNS)


def mark_attendance(student_id: str, student_name: str) -> bool:
    """
    Mark attendance for a student.
    Returns True if attendance was marked, False if already marked today.
    """
    init_attendance_csv()
    df = load_attendance()

    today = datetime.now().strftime("%Y-%m-%d")
    now_time = datetime.now().strftime("%H:%M:%S")

    # Check if already marked today
    already_marked = (
        not df.empty
        and ((df["Student ID"].astype(str) == str(student_id)) &
             (df["Date"] == today)).any()
    )

    if already_marked:
        return False  # Already marked

    # Append new record
    new_row = pd.DataFrame([{
        "Student ID": student_id,
        "Student Name": student_name,
        "Date": today,
        "Time": now_time,
        "Status": "Present"
    }])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(ATTENDANCE_CSV, index=False)
    return True


def search_student_attendance(query: str) -> pd.DataFrame:
    """Search attendance records by student ID or name (case-insensitive)."""
    df = load_attendance()
    if df.empty:
        return df
    query = query.strip().lower()
    mask = (
        df["Student ID"].astype(str).str.lower().str.contains(query) |
        df["Student Name"].astype(str).str.lower().str.contains(query)
    )
    return df[mask].reset_index(drop=True)


# ── Encodings (face data) ──────────────────────────────────────────────────────

def load_encodings() -> dict:
    """
    Load saved face encodings from pickle file.
    Returns dict: { student_id: {"name": str, "encodings": [list of encodings]} }
    """
    if not os.path.exists(ENCODINGS_FILE):
        return {}
    try:
        with open(ENCODINGS_FILE, "rb") as f:
            return pickle.load(f)
    except Exception as e:
        print(f"[DB] Error loading encodings: {e}")
        return {}


def save_encodings(data: dict):
    """Save face encodings dictionary to pickle file."""
    ensure_directories()
    try:
        with open(ENCODINGS_FILE, "wb") as f:
            pickle.dump(data, f)
    except Exception as e:
        print(f"[DB] Error saving encodings: {e}")


def student_id_exists(student_id: str) -> bool:
    """Check if a student ID already exists in the encodings database."""
    data = load_encodings()
    return str(student_id) in data


def register_student_encoding(student_id: str, name: str, encodings: list):
    """Add or update a student's face encodings in the database."""
    data = load_encodings()
    data[str(student_id)] = {
        "name": name,
        "encodings": encodings
    }
    save_encodings(data)


def get_all_students() -> list:
    """Return list of all registered students as (id, name) tuples."""
    data = load_encodings()
    return [(sid, info["name"]) for sid, info in data.items()]
