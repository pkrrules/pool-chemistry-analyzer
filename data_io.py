"""
Loading the default synthetic history and validating an uploaded CSV against
the schema in thresholds.py. Shared by app.py and tabs/upload_tab.py.
"""

from pathlib import Path

import pandas as pd
import streamlit as st

from thresholds import DATE_COLUMN, REQUIRED_COLUMNS

DATA_DIR = Path(__file__).resolve().parent / "data"
HISTORY_PATH = DATA_DIR / "pool_chemistry_history.csv"
TEMPLATE_PATH = DATA_DIR / "csv_upload_template.csv"


class CsvValidationError(Exception):
    """Raised when an uploaded CSV doesn't match the expected schema."""


@st.cache_data
def load_default_history() -> pd.DataFrame:
    df = pd.read_csv(HISTORY_PATH, parse_dates=[DATE_COLUMN])
    return df.sort_values(DATE_COLUMN).reset_index(drop=True)


def validate_and_parse(uploaded_file) -> pd.DataFrame:
    """Parse an uploaded CSV, raising CsvValidationError with a clear message
    on any schema problem. Returns a clean, date-sorted DataFrame on success.
    """
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as exc:
        raise CsvValidationError(f"Could not read this file as a CSV: {exc}") from exc

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise CsvValidationError(
            "Missing required column(s): " + ", ".join(missing)
            + f". Expected columns: {', '.join(REQUIRED_COLUMNS)}."
        )

    try:
        df[DATE_COLUMN] = pd.to_datetime(df[DATE_COLUMN])
    except Exception as exc:
        raise CsvValidationError(f"Could not parse '{DATE_COLUMN}' as dates: {exc}") from exc

    numeric_cols = [c for c in REQUIRED_COLUMNS if c != DATE_COLUMN]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    bad_cols = [c for c in numeric_cols if df[c].isna().any()]
    if bad_cols:
        raise CsvValidationError(
            "Non-numeric or missing values found in: " + ", ".join(bad_cols)
        )

    if df.empty:
        raise CsvValidationError("The uploaded CSV has no data rows.")

    return df.sort_values(DATE_COLUMN).reset_index(drop=True)
