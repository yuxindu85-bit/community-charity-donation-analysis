import os
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_ROOT / ".matplotlib_cache"))

import matplotlib.pyplot as plt


DATA_DIR = PROJECT_ROOT / "data"
REPORT_DIR = PROJECT_ROOT / "reports"
FIGURE_DIR = PROJECT_ROOT / "outputs" / "figures"


def load_data():
    donations = pd.read_csv(DATA_DIR / "donations.csv")
    sales = pd.read_csv(DATA_DIR / "sale_records.csv")

    donations["received_date"] = pd.to_datetime(donations["received_date"])
    sales["event_day"] = pd.to_datetime(sales["event_day"])
    sales["revenue_cny"] = sales["quantity"] * sales["unit_price_cny"]
    sales["net_contribution_cny"] = sales["revenue_cny"] - sales["cost_cny"]
    return donations, sales


def calculate_totals(donations, sales):
    total_direct_donations = donations["amount_cny"].sum()
    total_sale_revenue = sales["revenue_cny"].sum()
    total_sale_net = sales["net_contribution_cny"].sum()
    total_funds_raised = total_direct_donations + total_sale_revenue

    return {
        "total_direct_donations": total_direct_donations,
        "total_sale_revenue": total_sale_revenue,
        "total_sale_net": total_sale_net,
        "total_funds_raised": total_funds_raised,
    }


def make_summaries(donations, sales):
    donor_type_summary = (
        donations.groupby("donor_type", as_index=False)
        .agg(
            donor_count=("donor_id", "count"),
            direct_donation_cny=("amount_cny", "sum"),
        )
        .sort_values("direct_donation_cny", ascending=False)
    )

    category_summary = (
        sales.groupby("item_category", as_index=False)
        .agg(
            items_sold=("quantity", "sum"),
            sale_revenue_cny=("revenue_cny", "sum"),
            sale_net_contribution_cny=("net_contribution_cny", "sum"),
        )
        .sort_values("sale_revenue_cny", ascending=False)
    )

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
    team_summary = team_summary.sort_values("total_contribution_cny", ascending=False)

    daily_direct = donations.groupby("received_date", as_index=False).agg(
        direct_donation_cny=("amount_cny", "sum")
    )
    daily_direct = daily_direct.rename(columns={"received_date": "date"})

    daily_sales = sales.groupby("event_day", as_index=False).agg(
        sale_revenue_cny=("revenue_cny", "sum")
    )
    daily_sales = daily_sales.rename(columns={"event_day": "date"})

    daily_summary = daily_direct.merge(daily_sales, on="date", how="outer").fillna(0)
    daily_summary["total_contribution_cny"] = (
        daily_summary["direct_donation_cny"] + daily_summary["sale_revenue_cny"]
    )
    daily_summary = daily_summary.sort_values("date")

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
    plt.bar(team_summary["team"], team_summary["total_contribution_cny"])
    plt.title("Total Contribution by Team")
    plt.ylabel("Contribution (CNY)")
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "team_contribution.png", dpi=160)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.plot(daily_summary["date"], daily_summary["total_contribution_cny"], marker="o")
    plt.title("Daily Contribution Trend")
    plt.xlabel("Date")
    plt.ylabel("Contribution (CNY)")
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
- Estimated total funds raised: {totals['total_funds_raised']:,.0f} CNY

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
    print(f"Total funds raised: {totals['total_funds_raised']:,.0f} CNY")


if __name__ == "__main__":
    main()
