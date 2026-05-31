import os

os.environ.setdefault("MPLCONFIGDIR", ".matplotlib_cache")

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from utils import CHARTS_DIR, SUMMARY_DIR, ensure_directory, load_csv


def save_bar_chart(dataframe, x_column, y_column, title, xlabel, ylabel, output_path):
    plt.figure(figsize=(9, 5))
    plt.bar(dataframe[x_column], dataframe[y_column], color="#4C78A8")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()


def create_revenue_by_category_chart():
    revenue = load_csv(SUMMARY_DIR / "sales_by_category.csv")
    save_bar_chart(
        revenue,
        "item_category",
        "sale_revenue_cny",
        "Sale Revenue by Item Category",
        "Item category",
        "Revenue (CNY)",
        CHARTS_DIR / "revenue_by_category.png",
    )


def create_item_quantity_by_category_chart():
    categories = load_csv(SUMMARY_DIR / "category_summary.csv")
    save_bar_chart(
        categories,
        "item_category",
        "total_quantity",
        "Donated Item Quantity by Category",
        "Item category",
        "Quantity",
        CHARTS_DIR / "item_quantity_by_category.png",
    )


def create_team_contribution_chart():
    donation_by_team = load_csv(SUMMARY_DIR / "donation_by_team.csv")
    sales_by_team = load_csv(SUMMARY_DIR / "sales_by_team.csv")
    teams = donation_by_team.merge(sales_by_team, on="team", how="outer").fillna(0)
    plt.figure(figsize=(8, 5))
    plt.bar(teams["team"], teams["team_donation_cny"], label="Direct donations", color="#59A14F")
    plt.bar(
        teams["team"],
        teams["sale_revenue_cny"],
        bottom=teams["team_donation_cny"],
        label="Sale revenue",
        color="#F28E2B",
    )
    plt.title("Team Contribution Summary")
    plt.xlabel("Team")
    plt.ylabel("Contribution (CNY)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "team_contribution.png", dpi=160)
    plt.close()


def create_estimate_vs_actual_chart():
    estimates = load_csv(SUMMARY_DIR / "estimate_vs_actual_summary.csv")
    x_values = range(len(estimates))
    width = 0.38

    plt.figure(figsize=(10, 5))
    plt.bar(
        [x - width / 2 for x in x_values],
        estimates["estimated_sold_value_cny"],
        width=width,
        label="Estimated sold value",
        color="#76B7B2",
    )
    plt.bar(
        [x + width / 2 for x in x_values],
        estimates["actual_sale_total_cny"],
        width=width,
        label="Actual sale revenue",
        color="#E15759",
    )
    plt.title("Estimated Value vs Actual Sale Revenue")
    plt.xlabel("Item category")
    plt.ylabel("Value (CNY)")
    plt.xticks(list(x_values), estimates["item_category"], rotation=35, ha="right")
    plt.legend()
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "estimate_vs_actual_price.png", dpi=160)
    plt.close()


def create_booth_revenue_chart():
    booths = load_csv(SUMMARY_DIR / "booth_summary.csv")
    save_bar_chart(
        booths,
        "booth_area",
        "booth_revenue_cny",
        "Booth Revenue Comparison",
        "Booth area",
        "Revenue (CNY)",
        CHARTS_DIR / "booth_revenue_comparison.png",
    )


def create_donation_source_chart():
    donations = load_csv(SUMMARY_DIR / "donation_summary.csv")
    plt.figure(figsize=(7, 7))
    plt.pie(
        donations["total_donation_cny"],
        labels=donations["donor_type"],
        autopct="%1.1f%%",
        startangle=90,
    )
    plt.title("Direct Donation Source Breakdown")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "donation_source_breakdown.png", dpi=160)
    plt.close()


def remove_legacy_summary_tables():
    for file_name in ["team_summary.csv", "team_inventory_summary.csv", "sales_by_booth.csv"]:
        file_path = SUMMARY_DIR / file_name
        if file_path.exists():
            file_path.unlink()


def create_all_charts():
    ensure_directory(CHARTS_DIR)
    remove_legacy_summary_tables()
    create_revenue_by_category_chart()
    create_item_quantity_by_category_chart()
    create_team_contribution_chart()
    create_estimate_vs_actual_chart()
    create_booth_revenue_chart()
    create_donation_source_chart()

    print("Charts created.")
    print("Saved charts to reports/charts/")


if __name__ == "__main__":
    create_all_charts()
