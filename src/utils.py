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

BOOTH_MAP = {
    "booth a": "Booth A",
    "booth b": "Booth B",
    "booth c": "Booth C",
    "booth d": "Booth D",
    "shared table": "Shared Table",
}

PRIVATE_COLUMNS = {
    "real_name",
    "full_name",
    "phone_number",
    "email",
    "address",
    "school_name",
    "contact",
    "wechat_id",
    "payment_account",
    "qr_code",
}

CONFIRMED_PAYMENT_STATUSES = {"received", "verified"}


def get_project_root():
    return PROJECT_ROOT


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


def standardize_booth(value):
    if pd.isna(value):
        return "Unknown"
    key = str(value).strip().lower()
    return BOOTH_MAP.get(key, str(value).strip().title())


def calculate_total(series):
    return pd.to_numeric(series, errors="coerce").fillna(0).sum()


def filter_confirmed_donations(dataframe):
    statuses = dataframe["payment_status"].fillna("").astype(str).str.lower()
    return dataframe[statuses.isin(CONFIRMED_PAYMENT_STATUSES)].copy()


def safe_divide(numerator, denominator):
    if denominator == 0:
        return 0
    return numerator / denominator


def check_required_columns(dataframe, required_columns, dataset_name):
    missing_columns = sorted(set(required_columns) - set(dataframe.columns))
    if missing_columns:
        columns = ", ".join(missing_columns)
        raise ValueError(f"{dataset_name} is missing required columns: {columns}")


def check_no_private_columns(dataframe, dataset_name):
    private_matches = PRIVATE_COLUMNS.intersection(set(dataframe.columns))
    if private_matches:
        columns = ", ".join(sorted(private_matches))
        raise ValueError(f"{dataset_name} contains private columns: {columns}")


def format_currency(value):
    return f"¥{float(value):,.0f}"


def add_share_column(dataframe, value_column, share_column):
    result = dataframe.copy()
    total = calculate_total(result[value_column])
    if total == 0:
        result[share_column] = 0
    else:
        result[share_column] = (result[value_column] / total).round(4)
    return result
