import os
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_ROOT / ".matplotlib_cache"))

import matplotlib.pyplot as plt


DATA_DIR = PROJECT_ROOT / "data"
REPORT_DIR = PROJECT_ROOT / "reports"
FIGURE_DIR = PROJECT_ROOT / "outputs" / "figures"


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    donations = pd.read_csv(DATA_DIR / "donations.csv")
    sales = pd.read_csv(DATA_DIR / "sale_records.csv")

    donations["received_date"] = pd.to_datetime(donations["received_date"])
    sales["event_day"] = pd.to_datetime(sales["event_day"])
    sales["revenue_cny"] = sales["quantity"] * sales["unit_price_cny"]
    sales["net_contribution_cny"] = sales["revenue_cny"] - sales["cost_cny"]
    return donations, sales


def make_summaries(
    donations: pd.DataFrame, sales: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    donor_type_summary = (
        donations.groupby("donor_type", as_index=False)
        .agg(donor_count=("donor_id", "count"), direct_donation_cny=("amount_cny", "sum"))
        .sort_values("direct_donation_cny", ascending=False)
    )

    category_summary = (
        sales.groupby("item_category", as_index=False)
        .agg(
            units_sold=("quantity", "sum"),
            revenue_cny=("revenue_cny", "sum"),
            net_contribution_cny=("net_contribution_cny", "sum"),
        )
        .sort_values("revenue_cny", ascending=False)
    )

    donation_by_team = donations.groupby("team", as_index=False).agg(
        direct_donation_cny=("amount_cny", "sum")
    )
    sale_by_team = sales.groupby("team", as_index=False).agg(
        sale_revenue_cny=("revenue_cny", "sum"),
        sale_net_contribution_cny=("net_contribution_cny", "sum"),
    )
    team_summary = donation_by_team.merge(sale_by_team, on="team", how="outer").fillna(0)
    team_summary["total_contribution_cny"] = (
        team_summary["direct_donation_cny"] + team_summary["sale_net_contribution_cny"]
    )
    team_summary = team_summary.sort_values("total_contribution_cny", ascending=False)

    daily_direct = donations.groupby("received_date", as_index=False).agg(
        direct_donation_cny=("amount_cny", "sum")
    )
    daily_direct = daily_direct.rename(columns={"received_date": "date"})
    daily_sales = sales.groupby("event_day", as_index=False).agg(
        sale_net_contribution_cny=("net_contribution_cny", "sum")
    )
    daily_sales = daily_sales.rename(columns={"event_day": "date"})
    daily_summary = daily_direct.merge(daily_sales, on="date", how="outer").fillna(0)
    daily_summary["total_contribution_cny"] = (
        daily_summary["direct_donation_cny"] + daily_summary["sale_net_contribution_cny"]
    )
    daily_summary = daily_summary.sort_values("date")

    return donor_type_summary, category_summary, team_summary, daily_summary


def save_charts(
    donor_type_summary: pd.DataFrame,
    category_summary: pd.DataFrame,
    team_summary: pd.DataFrame,
    daily_summary: pd.DataFrame,
) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(7, 5))
    plt.bar(donor_type_summary["donor_type"], donor_type_summary["direct_donation_cny"])
    plt.title("Direct Donations by Donor Type")
    plt.ylabel("Amount (CNY)")
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "direct_donations_by_type.png", dpi=160)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.bar(category_summary["item_category"], category_summary["revenue_cny"])
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
    plt.ylabel("Contribution (CNY)")
    plt.xlabel("Date")
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "daily_contribution_trend.png", dpi=160)
    plt.close()


def write_report(
    donations: pd.DataFrame,
    sales: pd.DataFrame,
    donor_type_summary: pd.DataFrame,
    category_summary: pd.DataFrame,
    team_summary: pd.DataFrame,
) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    total_direct = donations["amount_cny"].sum()
    total_sale_revenue = sales["revenue_cny"].sum()
    total_sale_net = sales["net_contribution_cny"].sum()
    total_available = total_direct + total_sale_net

    top_donor_type = donor_type_summary.iloc[0]["donor_type"]
    top_category = category_summary.iloc[0]["item_category"]
    top_team = team_summary.iloc[0]["team"]

    report = f"""# Community Charity Event Summary

## Overview

I used this anonymized dataset to review a community charity event for
special-needs children and elderly people living alone. The dataset includes
{len(donations)} direct donation records and {len(sales)} sale records.
Direct donations totaled {total_direct:.0f} CNY. The charity sale created
{total_sale_revenue:.0f} CNY in revenue and {total_sale_net:.0f} CNY in net
contribution after simple item costs.

The estimated amount available for the charity purpose was {total_available:.0f}
CNY.

## Main Findings

Finding 1: The largest direct donation source was {top_donor_type}.

Finding 2: The highest-revenue sale category was {top_category}.

Finding 3: {top_team} had the highest combined contribution from direct
donations and sale activity.

## My Reflection

This analysis is small, but it helped me see where the money came from and which
records need to be kept more carefully. For the next event, I would record item
costs earlier and keep separate notes for direct donations and charity sale
income.
"""
    (REPORT_DIR / "event_summary.md").write_text(report, encoding="utf-8")


def main() -> None:
    donations, sales = load_data()
    summaries = make_summaries(donations, sales)
    donor_type_summary, category_summary, team_summary, daily_summary = summaries

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    donor_type_summary.to_csv(REPORT_DIR / "donor_type_summary.csv", index=False)
    category_summary.to_csv(REPORT_DIR / "category_summary.csv", index=False)
    team_summary.to_csv(REPORT_DIR / "team_summary.csv", index=False)
    daily_summary.to_csv(REPORT_DIR / "daily_summary.csv", index=False)

    save_charts(donor_type_summary, category_summary, team_summary, daily_summary)
    write_report(donations, sales, donor_type_summary, category_summary, team_summary)

    total_direct = donations["amount_cny"].sum()
    total_sale_net = sales["net_contribution_cny"].sum()
    print("Analysis finished.")
    print(f"Direct donations: {total_direct:.0f} CNY")
    print(f"Net charity sale contribution: {total_sale_net:.0f} CNY")
    print(f"Estimated available amount: {total_direct + total_sale_net:.0f} CNY")


if __name__ == "__main__":
    main()
