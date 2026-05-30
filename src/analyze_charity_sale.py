import os
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_ROOT / ".matplotlib_cache"))

import matplotlib.pyplot as plt


DATA_DIR = PROJECT_ROOT / "data"
REPORT_DIR = PROJECT_ROOT / "reports"
FIGURE_DIR = PROJECT_ROOT / "outputs" / "figures"

DONATION_COLUMNS = {
    "record_id",
    "received_date",
    "team",
    "donor_id",
    "donor_type",
    "amount_cny",
    "payment_status",
}

SALE_COLUMNS = {
    "sale_id",
    "event_day",
    "team",
    "item_category",
    "quantity",
    "unit_price_cny",
    "cost_cny",
}


def validate_columns(dataframe, required_columns, file_name):
    missing_columns = sorted(required_columns - set(dataframe.columns))
    if missing_columns:
        missing_text = ", ".join(missing_columns)
        raise ValueError(f"{file_name} is missing columns: {missing_text}")


def load_data():
    donations = pd.read_csv(DATA_DIR / "donations.csv")
    sales = pd.read_csv(DATA_DIR / "sale_records.csv")

    validate_columns(donations, DONATION_COLUMNS, "donations.csv")
    validate_columns(sales, SALE_COLUMNS, "sale_records.csv")

    donations["received_date"] = pd.to_datetime(donations["received_date"])
    sales["event_day"] = pd.to_datetime(sales["event_day"])

    donations["amount_cny"] = pd.to_numeric(donations["amount_cny"], errors="coerce")
    sales["quantity"] = pd.to_numeric(sales["quantity"], errors="coerce")
    sales["unit_price_cny"] = pd.to_numeric(sales["unit_price_cny"], errors="coerce")
    sales["cost_cny"] = pd.to_numeric(sales["cost_cny"], errors="coerce").fillna(0)

    if donations["amount_cny"].isna().any():
        raise ValueError("donations.csv contains invalid donation amounts.")
    if sales[["quantity", "unit_price_cny"]].isna().any().any():
        raise ValueError("sale_records.csv contains invalid sale values.")
    if (donations["amount_cny"] <= 0).any():
        raise ValueError("Donation amounts must be positive.")
    if (sales["quantity"] <= 0).any() or (sales["unit_price_cny"] <= 0).any():
        raise ValueError("Sale quantity and unit price must be positive.")

    sales["revenue_cny"] = sales["quantity"] * sales["unit_price_cny"]
    sales["net_contribution_cny"] = sales["revenue_cny"] - sales["cost_cny"]
    sales["margin_rate"] = sales["net_contribution_cny"] / sales["revenue_cny"]

    return donations, sales


def calculate_totals(donations, sales):
    total_direct_donations = donations["amount_cny"].sum()
    total_sale_revenue = sales["revenue_cny"].sum()
    total_sale_cost = sales["cost_cny"].sum()
    total_sale_net = sales["net_contribution_cny"].sum()
    total_funds_raised = total_direct_donations + total_sale_revenue
    estimated_available_after_cost = total_direct_donations + total_sale_net

    return {
        "total_direct_donations": total_direct_donations,
        "total_sale_revenue": total_sale_revenue,
        "total_sale_cost": total_sale_cost,
        "total_sale_net": total_sale_net,
        "total_funds_raised": total_funds_raised,
        "estimated_available_after_cost": estimated_available_after_cost,
    }


def make_summaries(donations, sales):
    totals = calculate_totals(donations, sales)

    donor_type_summary = (
        donations.groupby("donor_type", as_index=False)
        .agg(
            donor_count=("donor_id", "count"),
            direct_donation_cny=("amount_cny", "sum"),
            average_donation_cny=("amount_cny", "mean"),
        )
        .sort_values("direct_donation_cny", ascending=False)
    )
    donor_type_summary["donation_share"] = (
        donor_type_summary["direct_donation_cny"] / totals["total_direct_donations"]
    ).round(4)
    donor_type_summary["average_donation_cny"] = donor_type_summary[
        "average_donation_cny"
    ].round(2)

    category_summary = (
        sales.groupby("item_category", as_index=False)
        .agg(
            items_sold=("quantity", "sum"),
            sale_revenue_cny=("revenue_cny", "sum"),
            total_cost_cny=("cost_cny", "sum"),
            sale_net_contribution_cny=("net_contribution_cny", "sum"),
            average_unit_price_cny=("unit_price_cny", "mean"),
            median_unit_price_cny=("unit_price_cny", "median"),
        )
        .sort_values("sale_revenue_cny", ascending=False)
    )
    category_summary["revenue_share"] = (
        category_summary["sale_revenue_cny"] / totals["total_sale_revenue"]
    ).round(4)
    category_summary["average_unit_price_cny"] = category_summary[
        "average_unit_price_cny"
    ].round(2)

    donation_by_team = donations.groupby("team", as_index=False).agg(
        direct_donation_cny=("amount_cny", "sum")
    )
    sale_by_team = sales.groupby("team", as_index=False).agg(
        sale_revenue_cny=("revenue_cny", "sum"),
        sale_net_contribution_cny=("net_contribution_cny", "sum"),
        items_sold=("quantity", "sum"),
    )
    team_summary = donation_by_team.merge(sale_by_team, on="team", how="outer").fillna(0)
    team_summary["total_contribution_cny"] = (
        team_summary["direct_donation_cny"] + team_summary["sale_revenue_cny"]
    )
    team_summary["contribution_share"] = (
        team_summary["total_contribution_cny"] / totals["total_funds_raised"]
    ).round(4)
    team_summary = team_summary.sort_values("total_contribution_cny", ascending=False)
    team_summary["team_rank"] = range(1, len(team_summary) + 1)

    daily_direct = donations.groupby("received_date", as_index=False).agg(
        direct_donation_cny=("amount_cny", "sum")
    )
    daily_direct = daily_direct.rename(columns={"received_date": "date"})

    daily_sales = sales.groupby("event_day", as_index=False).agg(
        sale_revenue_cny=("revenue_cny", "sum"),
        sale_net_contribution_cny=("net_contribution_cny", "sum"),
    )
    daily_sales = daily_sales.rename(columns={"event_day": "date"})

    daily_summary = daily_direct.merge(daily_sales, on="date", how="outer").fillna(0)
    daily_summary["total_contribution_cny"] = (
        daily_summary["direct_donation_cny"] + daily_summary["sale_revenue_cny"]
    )
    daily_summary = daily_summary.sort_values("date")
    daily_summary["cumulative_contribution_cny"] = daily_summary[
        "total_contribution_cny"
    ].cumsum()

    return donor_type_summary, category_summary, team_summary, daily_summary


def save_summary_tables(donor_type_summary, category_summary, team_summary, daily_summary):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    donor_type_summary.to_csv(REPORT_DIR / "donor_type_summary.csv", index=False)
    category_summary.to_csv(REPORT_DIR / "category_summary.csv", index=False)
    team_summary.to_csv(REPORT_DIR / "team_summary.csv", index=False)
    daily_summary.to_csv(REPORT_DIR / "daily_summary.csv", index=False)


def save_charts(donor_type_summary, category_summary, team_summary, daily_summary):
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(7, 5))
    plt.bar(donor_type_summary["donor_type"], donor_type_summary["direct_donation_cny"])
    plt.title("Direct Donations by Donor Type")
    plt.ylabel("Amount (CNY)")
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "direct_donations_by_type.png", dpi=160)
    plt.close()

    plt.figure(figsize=(9, 5))
    plt.bar(category_summary["item_category"], category_summary["sale_revenue_cny"])
    plt.title("Charity Sale Revenue by Category")
    plt.ylabel("Revenue (CNY)")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "sale_revenue_by_category.png", dpi=160)
    plt.close()

    plt.figure(figsize=(7, 5))
    plt.bar(team_summary["team"], team_summary["direct_donation_cny"], label="Donations")
    plt.bar(
        team_summary["team"],
        team_summary["sale_revenue_cny"],
        bottom=team_summary["direct_donation_cny"],
        label="Sale Revenue",
    )
    plt.title("Team Contribution Breakdown")
    plt.ylabel("Contribution (CNY)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "team_contribution.png", dpi=160)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.plot(
        daily_summary["date"],
        daily_summary["cumulative_contribution_cny"],
        marker="o",
    )
    plt.title("Cumulative Contribution Trend")
    plt.xlabel("Date")
    plt.ylabel("Cumulative Contribution (CNY)")
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "daily_contribution_trend.png", dpi=160)
    plt.close()


def write_report(donations, sales, donor_type_summary, category_summary, team_summary):
    totals = calculate_totals(donations, sales)
    top_donor_type = donor_type_summary.iloc[0]["donor_type"]
    top_category = category_summary.iloc[0]["item_category"]
    top_team = team_summary.iloc[0]["team"]

    report = f"""# Community Charity Sale Summary

## Overview

This report summarizes anonymized donation and charity sale records from a
community charity sale. The project is a simple student data analysis project,
not an official financial audit.

## Main Results

- Direct donations: {totals['total_direct_donations']:,.0f} CNY
- Charity sale revenue: {totals['total_sale_revenue']:,.0f} CNY
- Estimated item costs: {totals['total_sale_cost']:,.0f} CNY
- Estimated available amount after sale costs: {totals['estimated_available_after_cost']:,.0f} CNY
- Total funds raised before sale costs: {totals['total_funds_raised']:,.0f} CNY

## Main Findings

- {top_donor_type} was the largest direct donation source.
- {top_category} produced the highest sale revenue.
- {top_team} had the highest combined contribution from donations and sales.

## Reflection

Working with the records helped me understand that charity sale work is not only
about collecting and selling items. Clear spreadsheets, item categories, team
records, and post-event review notes made the activity easier to organize and
explain afterward.
"""
    (REPORT_DIR / "event_summary.md").write_text(report, encoding="utf-8")


def main():
    donations, sales = load_data()
    donor_type_summary, category_summary, team_summary, daily_summary = make_summaries(
        donations, sales
    )

    save_summary_tables(donor_type_summary, category_summary, team_summary, daily_summary)
    save_charts(donor_type_summary, category_summary, team_summary, daily_summary)
    write_report(donations, sales, donor_type_summary, category_summary, team_summary)

    totals = calculate_totals(donations, sales)
    print("Analysis finished.")
    print(f"Direct donations: {totals['total_direct_donations']:,.0f} CNY")
    print(f"Charity sale revenue: {totals['total_sale_revenue']:,.0f} CNY")
    print(f"Estimated sale costs: {totals['total_sale_cost']:,.0f} CNY")
    print(
        "Estimated available amount after costs: "
        f"{totals['estimated_available_after_cost']:,.0f} CNY"
    )
    print(f"Total funds raised before costs: {totals['total_funds_raised']:,.0f} CNY")


if __name__ == "__main__":
    main()
