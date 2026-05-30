import os
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SUMMARY_DIR = PROJECT_ROOT / "reports" / "summary_tables"
CHART_DIR = PROJECT_ROOT / "reports" / "charts"

os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_ROOT / ".matplotlib_cache"))

import matplotlib.pyplot as plt


def load_summary_tables() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if not (SUMMARY_DIR / "category_summary.csv").exists():
        from analyze_charity_sale import main as analyze_main

        analyze_main()

    donation_summary = pd.read_csv(SUMMARY_DIR / "donation_summary.csv")
    category_summary = pd.read_csv(SUMMARY_DIR / "category_summary.csv")
    team_summary = pd.read_csv(SUMMARY_DIR / "team_summary.csv")
    return donation_summary, category_summary, team_summary


def save_revenue_by_category(category_summary: pd.DataFrame) -> None:
    plt.figure(figsize=(9, 5))
    plt.bar(category_summary["item_category"], category_summary["sale_revenue"])
    plt.title("Sale Revenue by Item Category")
    plt.xlabel("Item Category")
    plt.ylabel("Revenue (CNY)")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(CHART_DIR / "revenue_by_category.png", dpi=160)
    plt.close()


def save_item_quantity_by_category(category_summary: pd.DataFrame) -> None:
    plt.figure(figsize=(9, 5))
    plt.bar(category_summary["item_category"], category_summary["items_sold"])
    plt.title("Item Quantity Sold by Category")
    plt.xlabel("Item Category")
    plt.ylabel("Items Sold")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(CHART_DIR / "item_quantity_by_category.png", dpi=160)
    plt.close()


def save_team_contribution(team_summary: pd.DataFrame) -> None:
    plt.figure(figsize=(8, 5))
    plt.bar(team_summary["team"], team_summary["direct_donations"], label="Direct Donations")
    plt.bar(
        team_summary["team"],
        team_summary["sale_revenue"],
        bottom=team_summary["direct_donations"],
        label="Sale Revenue",
    )
    plt.title("Team Contribution")
    plt.xlabel("Team")
    plt.ylabel("Contribution (CNY)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(CHART_DIR / "team_contribution.png", dpi=160)
    plt.close()


def main() -> None:
    _, category_summary, team_summary = load_summary_tables()
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    save_revenue_by_category(category_summary)
    save_item_quantity_by_category(category_summary)
    save_team_contribution(team_summary)
    print(f"Saved charts to {CHART_DIR}")


if __name__ == "__main__":
    main()
