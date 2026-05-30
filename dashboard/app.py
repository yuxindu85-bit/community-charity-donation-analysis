import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
SUMMARY_DIR = PROJECT_ROOT / "reports" / "summary_tables"
METRICS_PATH = PROJECT_ROOT / "models" / "model_metrics.json"


@st.cache_data
def load_data():
    donations = pd.read_csv(PROCESSED_DIR / "cleaned_donations.csv")
    inventory = pd.read_csv(PROCESSED_DIR / "cleaned_inventory.csv")
    sales = pd.read_csv(PROCESSED_DIR / "cleaned_sales.csv")
    booths = pd.read_csv(PROCESSED_DIR / "cleaned_booth_layout.csv")
    merged = pd.read_csv(PROCESSED_DIR / "merged_event_data.csv")
    booth_summary = pd.read_csv(SUMMARY_DIR / "booth_summary.csv")
    team_summary = pd.read_csv(SUMMARY_DIR / "team_summary.csv")
    return donations, inventory, sales, booths, merged, booth_summary, team_summary


def apply_filters(inventory, sales, selected_team, selected_category, selected_booth, selected_condition):
    filtered_inventory = inventory.copy()
    filtered_sales = sales.copy()

    if selected_team != "All":
        filtered_inventory = filtered_inventory[filtered_inventory["team"] == selected_team]
        filtered_sales = filtered_sales[filtered_sales["team"] == selected_team]
    if selected_category != "All":
        filtered_inventory = filtered_inventory[
            filtered_inventory["item_category"] == selected_category
        ]
        filtered_sales = filtered_sales[filtered_sales["item_category"] == selected_category]
    if selected_booth != "All":
        filtered_inventory = filtered_inventory[filtered_inventory["booth_area"] == selected_booth]
        filtered_sales = filtered_sales[filtered_sales["booth_area"] == selected_booth]
    if selected_condition != "All":
        filtered_inventory = filtered_inventory[
            filtered_inventory["condition"] == selected_condition
        ]

    return filtered_inventory, filtered_sales


def show_bar_chart(dataframe, x_column, y_column, title):
    if dataframe.empty:
        st.info("No data available for the selected filters.")
        return
    chart = px.bar(dataframe, x=x_column, y=y_column, title=title)
    st.plotly_chart(chart, use_container_width=True)


def main():
    st.set_page_config(page_title="Community Charity Sale Data Dashboard", layout="wide")
    st.title("Community Charity Sale Data Dashboard")
    st.caption(
        "A student-built dashboard for reviewing anonymized charity sale data."
    )

    donations, inventory, sales, booths, merged, booth_summary, team_summary = load_data()

    st.sidebar.header("Filters")
    selected_team = st.sidebar.selectbox(
        "Team",
        ["All"] + sorted(inventory["team"].unique().tolist()),
    )
    selected_category = st.sidebar.selectbox(
        "Item category",
        ["All"] + sorted(inventory["item_category"].unique().tolist()),
    )
    selected_booth = st.sidebar.selectbox(
        "Booth area",
        ["All"] + sorted(inventory["booth_area"].unique().tolist()),
    )
    selected_condition = st.sidebar.selectbox(
        "Condition",
        ["All"] + sorted(inventory["condition"].unique().tolist()),
    )

    filtered_inventory, filtered_sales = apply_filters(
        inventory,
        sales,
        selected_team,
        selected_category,
        selected_booth,
        selected_condition,
    )

    total_direct_donations = donations["donation_amount_cny"].sum()
    total_sale_revenue = sales["total_sale_cny"].sum()
    total_funds = total_direct_donations + total_sale_revenue

    st.header("Key Metrics")
    columns = st.columns(6)
    columns[0].metric("Direct donations", f"¥{total_direct_donations:,.0f}")
    columns[1].metric("Sale revenue", f"¥{total_sale_revenue:,.0f}")
    columns[2].metric("Total funds", f"¥{total_funds:,.0f}")
    columns[3].metric("Categories", inventory["item_category"].nunique())
    columns[4].metric("Booths", inventory["booth_area"].nunique())
    columns[5].metric("Teams", inventory["team"].nunique())

    st.header("Donation Analysis")
    donation_by_type = (
        donations.groupby("donor_type", as_index=False)["donation_amount_cny"]
        .sum()
        .sort_values("donation_amount_cny", ascending=False)
    )
    donation_by_team = (
        donations.groupby("team", as_index=False)["donation_amount_cny"]
        .sum()
        .sort_values("donation_amount_cny", ascending=False)
    )
    col1, col2 = st.columns(2)
    with col1:
        show_bar_chart(
            donation_by_type,
            "donor_type",
            "donation_amount_cny",
            "Donation Amount by Donor Type",
        )
    with col2:
        show_bar_chart(
            donation_by_team,
            "team",
            "donation_amount_cny",
            "Donation Amount by Team",
        )

    st.header("Inventory Analysis")
    quantity_by_category = (
        filtered_inventory.groupby("item_category", as_index=False)["quantity"]
        .sum()
        .sort_values("quantity", ascending=False)
    )
    value_by_category = (
        filtered_inventory.groupby("item_category", as_index=False)[
            "estimated_total_value_cny"
        ]
        .sum()
        .sort_values("estimated_total_value_cny", ascending=False)
    )
    status_breakdown = (
        filtered_inventory.groupby("status", as_index=False)["quantity"]
        .sum()
        .sort_values("quantity", ascending=False)
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        show_bar_chart(quantity_by_category, "item_category", "quantity", "Item Quantity")
    with col2:
        show_bar_chart(
            value_by_category,
            "item_category",
            "estimated_total_value_cny",
            "Estimated Value by Category",
        )
    with col3:
        show_bar_chart(status_breakdown, "status", "quantity", "Item Status Breakdown")

    st.header("Sales Analysis")
    revenue_by_category = (
        filtered_sales.groupby("item_category", as_index=False)["total_sale_cny"]
        .sum()
        .sort_values("total_sale_cny", ascending=False)
    )
    revenue_by_booth = (
        filtered_sales.groupby("booth_area", as_index=False)["total_sale_cny"]
        .sum()
        .sort_values("total_sale_cny", ascending=False)
    )
    revenue_by_team = (
        filtered_sales.groupby("team", as_index=False)["total_sale_cny"]
        .sum()
        .sort_values("total_sale_cny", ascending=False)
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        show_bar_chart(
            revenue_by_category,
            "item_category",
            "total_sale_cny",
            "Sale Revenue by Category",
        )
    with col2:
        show_bar_chart(
            revenue_by_booth,
            "booth_area",
            "total_sale_cny",
            "Sale Revenue by Booth Area",
        )
    with col3:
        show_bar_chart(
            revenue_by_team,
            "team",
            "total_sale_cny",
            "Sale Revenue by Team",
        )

    st.header("Estimate vs Actual")
    price_data = sales.merge(
        inventory[["item_id", "estimated_unit_value_cny", "condition"]],
        on="item_id",
        how="left",
    )
    scatter = px.scatter(
        price_data,
        x="estimated_unit_value_cny",
        y="final_unit_price_cny",
        color="item_category",
        hover_data=["item_id", "booth_area", "team"],
        title="Estimated Unit Value vs Final Unit Price",
    )
    st.plotly_chart(scatter, use_container_width=True)

    estimate_table = (
        price_data.groupby("item_category", as_index=False)
        .agg(
            average_estimated_value=("estimated_unit_value_cny", "mean"),
            average_sale_price=("final_unit_price_cny", "mean"),
        )
        .round(2)
    )
    st.dataframe(estimate_table, use_container_width=True)

    st.header("Booth Layout Review")
    st.dataframe(
        booth_summary[
            [
                "booth_area",
                "assigned_team",
                "main_category",
                "estimated_items",
                "actual_items",
                "booth_revenue_cny",
            ]
        ],
        use_container_width=True,
    )

    st.header("Team Contribution")
    st.dataframe(team_summary, use_container_width=True)

    st.header("Machine Learning Results")
    if METRICS_PATH.exists():
        metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
        st.json(metrics)
    else:
        st.info("Run the model training scripts to generate model metrics.")

    st.warning(
        "The machine learning models are small exploratory learning models. "
        "They are not official financial or operational prediction tools."
    )


if __name__ == "__main__":
    main()
