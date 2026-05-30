from utils import DATA_PROCESSED_DIR, SUMMARY_DIR, add_share_column, load_csv, save_csv


def summarize_inventory(inventory):
    category_summary = (
        inventory.groupby("item_category", as_index=False)
        .agg(
            item_groups=("item_id", "count"),
            total_quantity=("quantity", "sum"),
            estimated_total_value_cny=("estimated_total_value_cny", "sum"),
        )
        .sort_values("estimated_total_value_cny", ascending=False)
    )
    category_summary = add_share_column(
        category_summary, "estimated_total_value_cny", "estimated_value_share"
    )

    status_summary = (
        inventory.groupby("status", as_index=False)
        .agg(
            item_groups=("item_id", "count"),
            total_quantity=("quantity", "sum"),
            estimated_total_value_cny=("estimated_total_value_cny", "sum"),
        )
        .sort_values("total_quantity", ascending=False)
    )

    team_inventory_summary = (
        inventory.groupby("team", as_index=False)
        .agg(
            item_groups=("item_id", "count"),
            total_quantity=("quantity", "sum"),
            estimated_total_value_cny=("estimated_total_value_cny", "sum"),
        )
        .sort_values("total_quantity", ascending=False)
    )

    return category_summary, status_summary, team_inventory_summary


def run_analysis():
    inventory = load_csv(DATA_PROCESSED_DIR / "cleaned_inventory.csv")
    category_summary, status_summary, team_inventory_summary = summarize_inventory(inventory)

    save_csv(category_summary, SUMMARY_DIR / "category_summary.csv")
    save_csv(status_summary, SUMMARY_DIR / "inventory_status_summary.csv")
    save_csv(team_inventory_summary, SUMMARY_DIR / "team_inventory_summary.csv")

    print("Inventory analysis finished.")
    print(f"Item groups: {len(inventory)}")
    print(f"Total donated item quantity: {inventory['quantity'].sum():,.0f}")


if __name__ == "__main__":
    run_analysis()
