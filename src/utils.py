from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"
SUMMARY_DIR = REPORTS_DIR / "summary_tables"
CHARTS_DIR = REPORTS_DIR / "charts"


CATEGORY_MAP = {
    "books": "Books",
    "clothes": "Clothes",
    "toys": "Toys",
    "handmade crafts": "Handmade Crafts",
    "electronics": "Electronics",
    "stationery": "Stationery",
    "accessories": "Accessories",
    "household items": "Household Items",
    "snacks": "Snacks",
}

TEAM_MAP = {
    "team a": "Team A",
    "team b": "Team B",
    "team c": "Team C",
    "team d": "Team D",
}


def ensure_directory(path):
    Path(path).mkdir(parents=True, exist_ok=True)


def load_csv(path):
    return pd.read_csv(path)


def save_csv(dataframe, path):
    ensure_directory(Path(path).parent)
    dataframe.to_csv(path, index=False)


def clean_text_columns(dataframe):
    cleaned = dataframe.copy()
    for column in cleaned.select_dtypes(include="object").columns:
        cleaned[column] = cleaned[column].fillna("").astype(str).str.strip()
    return cleaned


def standardize_category(value):
    if pd.isna(value):
        return "Unknown"
    key = str(value).strip().lower()
    return CATEGORY_MAP.get(key, str(value).strip().title())


def standardize_team(value):
    if pd.isna(value):
        return "Unknown"
    key = str(value).strip().lower()
    return TEAM_MAP.get(key, str(value).strip())


def calculate_total(series):
    return pd.to_numeric(series, errors="coerce").fillna(0).sum()


def add_share_column(dataframe, value_column, share_column):
    result = dataframe.copy()
    total = calculate_total(result[value_column])
    if total == 0:
        result[share_column] = 0
    else:
        result[share_column] = (result[value_column] / total).round(4)
    return result
