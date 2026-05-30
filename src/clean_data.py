from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
CLEANED_DATA_FILE = PROCESSED_DATA_DIR / "cleaned_charity_sale_data.csv"


TEAM_NAMES = {"team a": "Team A", "team b": "Team B", "team c": "Team C", "team d": "Team D"}


def standardize_team(value: object) -> str:
    text = str(value).strip()
    return TEAM_NAMES.get(text.lower(), text)


def standardize_category(value: object) -> str:
    text = str(value).strip()
    return " ".join(word.capitalize() for word in text.split())


def load_raw_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    donations = pd.read_csv(RAW_DATA_DIR / "donation_records_sample.csv")
    sales = pd.read_csv(RAW_DATA_DIR / "sale_records_sample.csv")
    inventory = pd.read_csv(RAW_DATA_DIR / "item_inventory_sample.csv")
    return donations, sales, inventory


def clean_donation_records(donations: pd.DataFrame) -> pd.DataFrame:
    cleaned = donations.copy()
    cleaned["donation_date"] = pd.to_datetime(cleaned["donation_date"])
    cleaned["team"] = cleaned["team"].apply(standardize_team)
    cleaned["donor_id"] = cleaned["donor_id"].fillna("Unknown_Donor").astype(str).str.strip()
    cleaned["donor_type"] = cleaned["donor_type"].fillna("Unknown").astype(str).str.strip()
    cleaned["donation_amount"] = pd.to_numeric(cleaned["donation_amount"], errors="coerce").fillna(0)
    cleaned = cleaned[cleaned["donation_amount"] > 0].reset_index(drop=True)
    return cleaned


def clean_inventory_records(inventory: pd.DataFrame) -> pd.DataFrame:
    cleaned = inventory.copy()
    cleaned["team"] = cleaned["team"].apply(standardize_team)
    cleaned["item_category"] = cleaned["item_category"].apply(standardize_category)
    cleaned["estimated_value"] = pd.to_numeric(cleaned["estimated_value"], errors="coerce").fillna(0)
    cleaned["quantity"] = pd.to_numeric(cleaned["quantity"], errors="coerce").fillna(0).astype(int)
    cleaned["booth_area"] = cleaned["booth_area"].fillna("Unassigned").astype(str).str.strip()
    cleaned["preparation_status"] = (
        cleaned["preparation_status"].fillna("Not Checked").astype(str).str.strip()
    )
    return cleaned


def clean_sale_records(sales: pd.DataFrame, inventory: pd.DataFrame) -> pd.DataFrame:
    cleaned = sales.copy()
    cleaned["sale_date"] = pd.to_datetime(cleaned["sale_date"])
    cleaned["team"] = cleaned["team"].apply(standardize_team)
    cleaned["item_category"] = cleaned["item_category"].apply(standardize_category)
    cleaned["quantity"] = pd.to_numeric(cleaned["quantity"], errors="coerce").fillna(0).astype(int)
    cleaned["final_sale_price"] = pd.to_numeric(
        cleaned["final_sale_price"], errors="coerce"
    ).fillna(0)
    cleaned = cleaned[(cleaned["quantity"] > 0) & (cleaned["final_sale_price"] > 0)].copy()
    cleaned["sale_revenue"] = cleaned["quantity"] * cleaned["final_sale_price"]

    inventory_lookup = inventory[
        ["item_id", "estimated_value", "booth_area", "preparation_status"]
    ].drop_duplicates("item_id")
    cleaned = cleaned.merge(inventory_lookup, on="item_id", how="left")
    cleaned["estimated_value"] = cleaned["estimated_value"].fillna(cleaned["final_sale_price"])
    cleaned["booth_area"] = cleaned["booth_area"].fillna("Unassigned")
    cleaned["preparation_status"] = cleaned["preparation_status"].fillna("Not Checked")
    return cleaned.reset_index(drop=True)


def build_cleaned_dataset(donations: pd.DataFrame, sales: pd.DataFrame) -> pd.DataFrame:
    donation_rows = pd.DataFrame(
        {
            "record_id": donations["record_id"],
            "record_type": "direct_donation",
            "date": donations["donation_date"],
            "team": donations["team"],
            "donor_id": donations["donor_id"],
            "donor_type": donations["donor_type"],
            "item_id": "",
            "item_category": "Direct Donation",
            "item_name": "",
            "quantity": 1,
            "estimated_value": donations["donation_amount"],
            "final_sale_price": 0,
            "amount_cny": donations["donation_amount"],
            "booth_area": "",
        }
    )

    sale_rows = pd.DataFrame(
        {
            "record_id": sales["sale_id"],
            "record_type": "charity_sale",
            "date": sales["sale_date"],
            "team": sales["team"],
            "donor_id": "",
            "donor_type": "",
            "item_id": sales["item_id"],
            "item_category": sales["item_category"],
            "item_name": sales["item_name"],
            "quantity": sales["quantity"],
            "estimated_value": sales["estimated_value"],
            "final_sale_price": sales["final_sale_price"],
            "amount_cny": sales["sale_revenue"],
            "booth_area": sales["booth_area"],
        }
    )

    cleaned = pd.concat([donation_rows, sale_rows], ignore_index=True)
    cleaned["date"] = pd.to_datetime(cleaned["date"]).dt.strftime("%Y-%m-%d")
    return cleaned.sort_values(["date", "record_type", "record_id"]).reset_index(drop=True)


def main() -> None:
    donations, sales, inventory = load_raw_data()
    clean_donations = clean_donation_records(donations)
    clean_inventory = clean_inventory_records(inventory)
    clean_sales = clean_sale_records(sales, clean_inventory)
    cleaned_dataset = build_cleaned_dataset(clean_donations, clean_sales)

    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    cleaned_dataset.to_csv(CLEANED_DATA_FILE, index=False)
    print(f"Saved cleaned data to {CLEANED_DATA_FILE}")


if __name__ == "__main__":
    main()
