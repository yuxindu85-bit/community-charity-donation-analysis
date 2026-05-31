from utils import DATA_PROCESSED_DIR, SUMMARY_DIR, add_share_column, load_csv, save_csv


def summarize_sales(sales, merged_event_data):
    revenue_by_category = (
        sales.groupby("item_category", as_index=False)
        .agg(
            records=("sale_id", "count"),
            quantity_sold=("quantity_sold", "sum"),
            sale_revenue_cny=("total_sale_cny", "sum"),
        )
        .sort_values("sale_revenue_cny", ascending=False)
    )
    revenue_by_category = add_share_column(
        revenue_by_category, "sale_revenue_cny", "revenue_share"
    )

    revenue_by_booth = (
        sales.groupby("booth_area", as_index=False)
        .agg(
            records=("sale_id", "count"),
            quantity_sold=("quantity_sold", "sum"),
            sale_revenue_cny=("total_sale_cny", "sum"),
        )
        .sort_values("sale_revenue_cny", ascending=False)
    )

    revenue_by_team = (
        sales.groupby("team", as_index=False)
        .agg(
            records=("sale_id", "count"),
            quantity_sold=("quantity_sold", "sum"),
            sale_revenue_cny=("total_sale_cny", "sum"),
        )
        .sort_values("sale_revenue_cny", ascending=False)
    )

    estimate_vs_actual = (
        merged_event_data.groupby("item_category", as_index=False)
        .agg(
            quantity_sold=("quantity_sold", "sum"),
            estimated_sold_value_cny=("estimated_sold_value_cny", "sum"),
            actual_sale_total_cny=("actual_sale_total_cny", "sum"),
            price_difference_cny=("price_difference_cny", "sum"),
        )
        .sort_values("actual_sale_total_cny", ascending=False)
    )
    estimate_vs_actual["actual_to_estimate_rate"] = (
        estimate_vs_actual["actual_sale_total_cny"]
        / estimate_vs_actual["estimated_sold_value_cny"].replace(0, 1)
    ).round(3)

    return revenue_by_category, revenue_by_booth, revenue_by_team, estimate_vs_actual


def summarize_team_contribution(donations, revenue_by_team):
    donation_by_team = (
        donations[donations["payment_status"].str.lower() == "received"]
        .groupby("team", as_index=False)
        .agg(direct_donation_cny=("donation_amount_cny", "sum"))
    )
    team_summary = donation_by_team.merge(revenue_by_team, on="team", how="outer").fillna(0)
    team_summary["total_contribution_cny"] = (
        team_summary["direct_donation_cny"] + team_summary["sale_revenue_cny"]
    )
    team_summary["team_rank"] = (
        team_summary["total_contribution_cny"].rank(method="dense", ascending=False).astype(int)
    )
    return team_summary.sort_values("total_contribution_cny", ascending=False)


def run_analysis():
    sales = load_csv(DATA_PROCESSED_DIR / "cleaned_sales.csv")
    donations = load_csv(DATA_PROCESSED_DIR / "cleaned_donations.csv")
    merged_event_data = load_csv(DATA_PROCESSED_DIR / "merged_event_data.csv")
    (
        revenue_by_category,
        revenue_by_booth,
        revenue_by_team,
        estimate_vs_actual,
    ) = summarize_sales(sales, merged_event_data)
    team_summary = summarize_team_contribution(donations, revenue_by_team)

    save_csv(revenue_by_category, SUMMARY_DIR / "sales_by_category.csv")
    save_csv(revenue_by_booth, SUMMARY_DIR / "sales_by_booth.csv")
    save_csv(revenue_by_team, SUMMARY_DIR / "sales_by_team.csv")
    save_csv(team_summary, SUMMARY_DIR / "team_summary.csv")
    save_csv(estimate_vs_actual, SUMMARY_DIR / "estimate_vs_actual_summary.csv")

    print("Sales analysis finished.")
    print(f"Total sale revenue: {sales['total_sale_cny'].sum():,.0f} CNY")
    print(f"Items sold: {sales['quantity_sold'].sum():,.0f}")


if __name__ == "__main__":
    run_analysis()
