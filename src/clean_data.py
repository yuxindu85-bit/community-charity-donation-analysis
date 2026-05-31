from utils import (
    DATA_PROCESSED_DIR,
    DATA_RAW_DIR,
    calculate_total,
    check_no_private_columns,
    check_required_columns,
    clean_text_columns,
    ensure_directory,
    load_csv,
    PRIVATE_COLUMNS,
    save_csv,
    standardize_booth,
    standardize_category,
    standardize_team,
)


DONATION_COLUMNS = {
    "donation_id",
    "donation_date",
    "donor_id",
    "donor_type",
    "team",
    "donation_amount_cny",
    "payment_status",
    "note",
}

INVENTORY_COLUMNS = {
    "item_id",
    "received_date",
    "item_category",
    "item_name",
    "quantity",
    "estimated_unit_value_cny",
    "condition",
    "team",
    "booth_area",
    "status",
}

SALE_COLUMNS = {
    "sale_id",
    "sale_date",
    "item_id",
    "item_category",
    "booth_area",
    "quantity_sold",
    "final_unit_price_cny",
    "total_sale_cny",
    "team",
    "payment_method",
}

BOOTH_COLUMNS = {
    "booth_id",
    "booth_area",
    "main_category",
    "assigned_team",
    "table_count",
    "estimated_items",
    "actual_items",
    "notes",
}


def check_private_columns(dataframes):
    for file_name, dataframe in dataframes.items():
        check_no_private_columns(dataframe, file_name)


def clean_donations(donations):
    cleaned = clean_text_columns(donations)
    cleaned["donation_date"] = cleaned["donation_date"].fillna("Unknown")
    cleaned["donor_type"] = cleaned["donor_type"].replace("", "Unknown")
    cleaned["team"] = cleaned["team"].apply(standardize_team)
    cleaned["donation_amount_cny"] = cleaned["donation_amount_cny"].fillna(0).astype(float)
    cleaned["payment_status"] = cleaned["payment_status"].replace("", "Unknown")

    if (cleaned["donation_amount_cny"] < 0).any():
        raise ValueError("Donation amounts cannot be negative.")

    return cleaned


def clean_inventory(inventory):
    cleaned = clean_text_columns(inventory)
    cleaned["item_category"] = cleaned["item_category"].apply(standardize_category)
    cleaned["team"] = cleaned["team"].apply(standardize_team)
    cleaned["booth_area"] = cleaned["booth_area"].apply(standardize_booth)
    cleaned["quantity"] = cleaned["quantity"].fillna(0).astype(int)
    cleaned["estimated_unit_value_cny"] = (
        cleaned["estimated_unit_value_cny"].fillna(0).astype(float)
    )
    cleaned["estimated_total_value_cny"] = (
        cleaned["quantity"] * cleaned["estimated_unit_value_cny"]
    )
    cleaned["condition"] = cleaned["condition"].replace("", "Unknown")
    cleaned["status"] = cleaned["status"].replace("", "Unknown")

    if (cleaned["quantity"] < 0).any():
        raise ValueError("Inventory quantity cannot be negative.")
    if (cleaned["estimated_unit_value_cny"] < 0).any():
        raise ValueError("Estimated unit value cannot be negative.")

    return cleaned


def clean_sales(sales):
    cleaned = clean_text_columns(sales)
    cleaned["item_category"] = cleaned["item_category"].apply(standardize_category)
    cleaned["team"] = cleaned["team"].apply(standardize_team)
    cleaned["booth_area"] = cleaned["booth_area"].apply(standardize_booth)
    cleaned["quantity_sold"] = cleaned["quantity_sold"].fillna(0).astype(int)
    cleaned["final_unit_price_cny"] = cleaned["final_unit_price_cny"].fillna(0).astype(float)
    cleaned["total_sale_cny"] = cleaned["total_sale_cny"].fillna(0).astype(float)

    expected_total = cleaned["quantity_sold"] * cleaned["final_unit_price_cny"]
    mismatched_rows = cleaned[cleaned["total_sale_cny"].round(2) != expected_total.round(2)]
    if not mismatched_rows.empty:
        ids = ", ".join(mismatched_rows["sale_id"].tolist())
        raise ValueError(f"Sale totals do not match quantity x unit price: {ids}")

    if (cleaned["quantity_sold"] < 0).any():
        raise ValueError("Quantity sold cannot be negative.")
    if (cleaned["final_unit_price_cny"] < 0).any():
        raise ValueError("Final unit price cannot be negative.")

    return cleaned


def clean_booth_layout(booths):
    cleaned = clean_text_columns(booths)
    cleaned["booth_area"] = cleaned["booth_area"].apply(standardize_booth)
    cleaned["assigned_team"] = cleaned["assigned_team"].apply(standardize_team)
    cleaned["table_count"] = cleaned["table_count"].fillna(0).astype(int)
    cleaned["estimated_items"] = cleaned["estimated_items"].fillna(0).astype(int)
    cleaned["actual_items"] = cleaned["actual_items"].fillna(0).astype(int)
    return cleaned


def validate_sale_item_ids(cleaned_inventory, cleaned_sales):
    inventory_ids = set(cleaned_inventory["item_id"])
    sale_ids = set(cleaned_sales["item_id"])
    missing_ids = sorted(sale_ids - inventory_ids)
    if missing_ids:
        ids = ", ".join(missing_ids)
        raise ValueError(f"Sales contain item IDs not found in inventory: {ids}")


def create_merged_event_data(cleaned_inventory, cleaned_sales):
    item_sales = (
        cleaned_sales.groupby("item_id", as_index=False)
        .agg(
            quantity_sold=("quantity_sold", "sum"),
            actual_sale_total_cny=("total_sale_cny", "sum"),
        )
    )
    merged = cleaned_inventory.merge(item_sales, on="item_id", how="left")
    merged["quantity_sold"] = merged["quantity_sold"].fillna(0).astype(int)
    merged["actual_sale_total_cny"] = merged["actual_sale_total_cny"].fillna(0)
    merged["estimated_sold_value_cny"] = (
        merged["quantity_sold"] * merged["estimated_unit_value_cny"]
    )
    merged["price_difference_cny"] = (
        merged["actual_sale_total_cny"] - merged["estimated_sold_value_cny"]
    )
    return merged


def run_cleaning():
    donations = load_csv(DATA_RAW_DIR / "donation_records_sample.csv")
    inventory = load_csv(DATA_RAW_DIR / "item_inventory_sample.csv")
    sales = load_csv(DATA_RAW_DIR / "sale_records_sample.csv")
    booths = load_csv(DATA_RAW_DIR / "booth_layout_sample.csv")

    check_required_columns(donations, DONATION_COLUMNS, "donation_records_sample.csv")
    check_required_columns(inventory, INVENTORY_COLUMNS, "item_inventory_sample.csv")
    check_required_columns(sales, SALE_COLUMNS, "sale_records_sample.csv")
    check_required_columns(booths, BOOTH_COLUMNS, "booth_layout_sample.csv")

    check_private_columns(
        {
            "donation_records_sample.csv": donations,
            "item_inventory_sample.csv": inventory,
            "sale_records_sample.csv": sales,
            "booth_layout_sample.csv": booths,
        }
    )

    cleaned_donations = clean_donations(donations)
    cleaned_inventory = clean_inventory(inventory)
    cleaned_sales = clean_sales(sales)
    cleaned_booths = clean_booth_layout(booths)
    validate_sale_item_ids(cleaned_inventory, cleaned_sales)
    merged_event_data = create_merged_event_data(cleaned_inventory, cleaned_sales)

    ensure_directory(DATA_PROCESSED_DIR)
    save_csv(cleaned_donations, DATA_PROCESSED_DIR / "cleaned_donations.csv")
    save_csv(cleaned_inventory, DATA_PROCESSED_DIR / "cleaned_inventory.csv")
    save_csv(cleaned_sales, DATA_PROCESSED_DIR / "cleaned_sales.csv")
    save_csv(cleaned_booths, DATA_PROCESSED_DIR / "cleaned_booth_layout.csv")
    save_csv(merged_event_data, DATA_PROCESSED_DIR / "merged_event_data.csv")

    print("Cleaning finished.")
    print(f"Donation records: {len(cleaned_donations)}")
    print(f"Inventory item groups: {len(cleaned_inventory)}")
    print(f"Sale records: {len(cleaned_sales)}")
    print(f"Booth records: {len(cleaned_booths)}")
    print(f"Total direct donations: {calculate_total(cleaned_donations['donation_amount_cny']):,.0f} CNY")
    print(f"Total sale revenue: {calculate_total(cleaned_sales['total_sale_cny']):,.0f} CNY")
    total_funds = calculate_total(cleaned_donations["donation_amount_cny"]) + calculate_total(
        cleaned_sales["total_sale_cny"]
    )
    print(f"Total funds raised: {total_funds:,.0f} CNY")


if __name__ == "__main__":
    run_cleaning()
