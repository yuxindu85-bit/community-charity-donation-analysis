import sys
import unittest
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from clean_data import run_cleaning
from utils import DATA_PROCESSED_DIR, DATA_RAW_DIR, PRIVATE_COLUMNS


class CleanDataTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        run_cleaning()

    def test_all_raw_data_files_exist(self):
        expected_files = [
            "donation_records_sample.csv",
            "item_inventory_sample.csv",
            "sale_records_sample.csv",
            "booth_layout_sample.csv",
        ]
        for file_name in expected_files:
            self.assertTrue((DATA_RAW_DIR / file_name).exists())

    def test_cleaned_data_files_are_generated(self):
        expected_files = [
            "cleaned_donations.csv",
            "cleaned_inventory.csv",
            "cleaned_sales.csv",
            "cleaned_booth_layout.csv",
            "merged_event_data.csv",
        ]
        for file_name in expected_files:
            self.assertTrue((DATA_PROCESSED_DIR / file_name).exists())

    def test_sale_totals_match_quantity_times_price(self):
        sales = pd.read_csv(DATA_PROCESSED_DIR / "cleaned_sales.csv")
        expected_total = sales["quantity_sold"] * sales["final_unit_price_cny"]
        self.assertTrue((sales["total_sale_cny"].round(2) == expected_total.round(2)).all())

    def test_sale_item_ids_match_inventory_item_ids(self):
        inventory = pd.read_csv(DATA_PROCESSED_DIR / "cleaned_inventory.csv")
        sales = pd.read_csv(DATA_PROCESSED_DIR / "cleaned_sales.csv")
        self.assertTrue(set(sales["item_id"]).issubset(set(inventory["item_id"])))

    def test_sale_records_match_inventory_category_booth_and_team(self):
        inventory = pd.read_csv(DATA_PROCESSED_DIR / "cleaned_inventory.csv")
        sales = pd.read_csv(DATA_PROCESSED_DIR / "cleaned_sales.csv")
        inventory_lookup = inventory[
            ["item_id", "item_category", "booth_area", "team"]
        ].rename(
            columns={
                "item_category": "inventory_category",
                "booth_area": "inventory_booth_area",
                "team": "inventory_team",
            }
        )
        merged = sales.merge(inventory_lookup, on="item_id", how="left")

        self.assertTrue((merged["item_category"] == merged["inventory_category"]).all())
        self.assertTrue((merged["booth_area"] == merged["inventory_booth_area"]).all())
        self.assertTrue((merged["team"] == merged["inventory_team"]).all())

    def test_quantity_sold_does_not_exceed_inventory_quantity(self):
        inventory = pd.read_csv(DATA_PROCESSED_DIR / "cleaned_inventory.csv")
        sales = pd.read_csv(DATA_PROCESSED_DIR / "cleaned_sales.csv")
        sold_by_item = (
            sales.groupby("item_id", as_index=False)
            .agg(total_quantity_sold=("quantity_sold", "sum"))
            .merge(inventory[["item_id", "quantity"]], on="item_id", how="left")
        )
        self.assertTrue(
            (sold_by_item["total_quantity_sold"] <= sold_by_item["quantity"]).all()
        )

    def test_category_names_are_standardized(self):
        inventory = pd.read_csv(DATA_PROCESSED_DIR / "cleaned_inventory.csv")
        expected_categories = {
            "Books",
            "Clothes",
            "Toys",
            "Handmade Crafts",
            "Electronics",
            "Stationery",
            "Accessories",
            "Household Items",
            "Snacks",
        }
        self.assertTrue(set(inventory["item_category"]).issubset(expected_categories))

    def test_no_private_information_columns_exist(self):
        files_to_check = [
            DATA_RAW_DIR / "donation_records_sample.csv",
            DATA_RAW_DIR / "item_inventory_sample.csv",
            DATA_RAW_DIR / "sale_records_sample.csv",
            DATA_RAW_DIR / "booth_layout_sample.csv",
            DATA_PROCESSED_DIR / "cleaned_donations.csv",
            DATA_PROCESSED_DIR / "cleaned_inventory.csv",
            DATA_PROCESSED_DIR / "cleaned_sales.csv",
            DATA_PROCESSED_DIR / "cleaned_booth_layout.csv",
        ]
        for file_path in files_to_check:
            dataframe = pd.read_csv(file_path)
            self.assertFalse(PRIVATE_COLUMNS.intersection(dataframe.columns))

    def test_required_columns_exist_after_cleaning(self):
        expected_columns = {
            "cleaned_donations.csv": {
                "donation_id",
                "donor_id",
                "donor_type",
                "team",
                "donation_amount_cny",
            },
            "cleaned_inventory.csv": {
                "item_id",
                "item_category",
                "quantity",
                "estimated_unit_value_cny",
                "estimated_total_value_cny",
            },
            "cleaned_sales.csv": {
                "sale_id",
                "item_id",
                "quantity_sold",
                "final_unit_price_cny",
                "total_sale_cny",
            },
        }

        for file_name, columns in expected_columns.items():
            dataframe = pd.read_csv(DATA_PROCESSED_DIR / file_name)
            self.assertTrue(columns.issubset(set(dataframe.columns)))


if __name__ == "__main__":
    unittest.main()
