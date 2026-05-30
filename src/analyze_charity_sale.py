from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLEANED_DATA_FILE = PROJECT_ROOT / "data" / "processed" / "cleaned_charity_sale_data.csv"
SUMMARY_DIR = PROJECT_ROOT / "reports" / "summary_tables"
REPORT_FILE = PROJECT_ROOT / "reports" / "final_charity_sale_report.md"


def load_cleaned_data() -> pd.DataFrame:
    if not CLEANED_DATA_FILE.exists():
        from clean_data import main as clean_data_main

        clean_data_main()

    data = pd.read_csv(CLEANED_DATA_FILE)
    data["date"] = pd.to_datetime(data["date"])
    return data


def calculate_total_donations(data: pd.DataFrame) -> float:
    donation_rows = data[data["record_type"] == "direct_donation"]
    return float(donation_rows["amount_cny"].sum())


def calculate_total_sale_revenue(data: pd.DataFrame) -> float:
    sale_rows = data[data["record_type"] == "charity_sale"]
    return float(sale_rows["amount_cny"].sum())


def calculate_total_funds_raised(data: pd.DataFrame) -> float:
    return calculate_total_donations(data) + calculate_total_sale_revenue(data)


def create_donation_summary(data: pd.DataFrame) -> pd.DataFrame:
    donation_rows = data[data["record_type"] == "direct_donation"].copy()
    summary = (
        donation_rows.groupby("donor_type", as_index=False)
        .agg(
            donor_count=("donor_id", "count"),
            donation_amount=("amount_cny", "sum"),
        )
        .sort_values("donation_amount", ascending=False)
    )
    return summary


def create_category_summary(data: pd.DataFrame) -> pd.DataFrame:
    sale_rows = data[data["record_type"] == "charity_sale"].copy()
    summary = (
        sale_rows.groupby("item_category", as_index=False)
        .agg(
            items_sold=("quantity", "sum"),
            sale_revenue=("amount_cny", "sum"),
            average_price=("final_sale_price", "mean"),
        )
        .sort_values("sale_revenue", ascending=False)
    )
    summary["average_price"] = summary["average_price"].round(2)
    return summary


def create_team_summary(data: pd.DataFrame) -> pd.DataFrame:
    donation_rows = data[data["record_type"] == "direct_donation"]
    sale_rows = data[data["record_type"] == "charity_sale"]

    donation_summary = donation_rows.groupby("team", as_index=False).agg(
        direct_donations=("amount_cny", "sum")
    )
    sale_summary = sale_rows.groupby("team", as_index=False).agg(
        sale_revenue=("amount_cny", "sum"),
        items_sold=("quantity", "sum"),
    )
    summary = donation_summary.merge(sale_summary, on="team", how="outer").fillna(0)
    summary["total_contribution"] = summary["direct_donations"] + summary["sale_revenue"]
    summary = summary.sort_values("total_contribution", ascending=False)
    return summary


def save_summary_tables(
    donation_summary: pd.DataFrame,
    category_summary: pd.DataFrame,
    team_summary: pd.DataFrame,
) -> None:
    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
    donation_summary.to_csv(SUMMARY_DIR / "donation_summary.csv", index=False)
    category_summary.to_csv(SUMMARY_DIR / "category_summary.csv", index=False)
    team_summary.to_csv(SUMMARY_DIR / "team_summary.csv", index=False)


def format_donor_type_label(donor_type: str) -> str:
    labels = {
        "Individual": "The individual donor group",
        "Local Business": "local business donors",
        "Community Group": "community groups",
    }
    return labels.get(donor_type, donor_type)


def write_final_report(
    data: pd.DataFrame,
    donation_summary: pd.DataFrame,
    category_summary: pd.DataFrame,
    team_summary: pd.DataFrame,
) -> None:
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    total_donations = calculate_total_donations(data)
    total_sale_revenue = calculate_total_sale_revenue(data)
    total_funds = calculate_total_funds_raised(data)
    top_donor_type = format_donor_type_label(donation_summary.iloc[0]["donor_type"])
    top_category = category_summary.iloc[0]["item_category"]
    top_team = team_summary.iloc[0]["team"]

    report = f"""# Final Charity Sale Report

## Overview

This report summarizes an anonymized charity sale dataset. The event combined
direct donations with income from donated items. In this sample dataset, direct
donations totaled {total_donations:,.0f} CNY and charity sale revenue totaled
{total_sale_revenue:,.0f} CNY. The combined total was {total_funds:,.0f} CNY.

## Data Sources

The project uses three sample CSV files:

- `donation_records_sample.csv` for direct donation records
- `sale_records_sample.csv` for sold item records
- `item_inventory_sample.csv` for item categories, estimated values, and booth
  planning information

All private names, phone numbers, school names, and organization names were
removed or replaced with anonymous labels before analysis.

## Main Findings

- {top_donor_type} was the largest direct donation source.
- {top_category} produced the highest sale revenue among item categories.
- {top_team} had the highest combined contribution from donations and sales.
- Direct donations were larger than sale revenue, which makes sense because a
  few donors gave larger one-time amounts while most sale items were lower-priced
  donated goods.

## How The Data Supported Event Planning

Keeping item and donation records in spreadsheets made the event easier to
organize. The item categories helped with booth layout, the estimated values
helped with price planning, and the team summaries helped review preparation
work after the event.

## Limitations

This is not an official financial audit. The dataset is a cleaned and anonymized
learning version of the event records. Some item descriptions were simplified,
and the data does not include exact sale time for each item.

## Future Improvements

- Track item IDs more carefully from donation to sale.
- Compare estimated item value with final sale price.
- Add booth-level or time-level sale information.
- Add more tests for category and team totals.

## Reflection

This project helped me understand that community service also depends on clear
organization. Counting items, cleaning records, and checking totals made the
post-event review more useful than a simple list of numbers.
"""
    REPORT_FILE.write_text(report, encoding="utf-8")


def main() -> None:
    data = load_cleaned_data()
    donation_summary = create_donation_summary(data)
    category_summary = create_category_summary(data)
    team_summary = create_team_summary(data)

    save_summary_tables(donation_summary, category_summary, team_summary)
    write_final_report(data, donation_summary, category_summary, team_summary)

    print("Analysis finished.")
    print(f"Direct donations: {calculate_total_donations(data):,.0f} CNY")
    print(f"Sale revenue: {calculate_total_sale_revenue(data):,.0f} CNY")
    print(f"Total funds raised: {calculate_total_funds_raised(data):,.0f} CNY")


if __name__ == "__main__":
    main()
