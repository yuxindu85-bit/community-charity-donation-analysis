from utils import DATA_PROCESSED_DIR, SUMMARY_DIR, load_csv, save_csv


def summarize_booths(booth_layout, sales):
    layout_summary = (
        booth_layout.groupby("booth_area", as_index=False)
        .agg(
            booth_id=("booth_id", lambda values: "; ".join(values)),
            main_category=("main_category", lambda values: "; ".join(values)),
            assigned_team=("assigned_team", lambda values: "; ".join(sorted(set(values)))),
            table_count=("table_count", "sum"),
            estimated_items=("estimated_items", "sum"),
            actual_items=("actual_items", "sum"),
            notes=("notes", lambda values: " | ".join(values)),
        )
    )

    booth_revenue = (
        sales.groupby("booth_area", as_index=False)
        .agg(
            sale_records=("sale_id", "count"),
            quantity_sold=("quantity_sold", "sum"),
            booth_revenue_cny=("total_sale_cny", "sum"),
        )
        .sort_values("booth_revenue_cny", ascending=False)
    )

    booth_summary = layout_summary.merge(booth_revenue, on="booth_area", how="left")
    booth_summary[["sale_records", "quantity_sold", "booth_revenue_cny"]] = booth_summary[
        ["sale_records", "quantity_sold", "booth_revenue_cny"]
    ].fillna(0)
    booth_summary["item_count_difference"] = (
        booth_summary["actual_items"] - booth_summary["estimated_items"]
    )
    booth_summary["revenue_per_actual_item_cny"] = (
        booth_summary["booth_revenue_cny"] / booth_summary["actual_items"].replace(0, 1)
    ).round(2)

    return booth_summary.sort_values("booth_revenue_cny", ascending=False)


def run_analysis():
    booth_layout = load_csv(DATA_PROCESSED_DIR / "cleaned_booth_layout.csv")
    sales = load_csv(DATA_PROCESSED_DIR / "cleaned_sales.csv")
    booth_summary = summarize_booths(booth_layout, sales)

    save_csv(booth_summary, SUMMARY_DIR / "booth_summary.csv")

    top_booth = booth_summary.iloc[0]
    print("Booth layout analysis finished.")
    print(
        f"Top booth by revenue: {top_booth['booth_area']} "
        f"({top_booth['booth_revenue_cny']:,.0f} CNY)"
    )


if __name__ == "__main__":
    run_analysis()
