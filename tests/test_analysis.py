import sys
import unittest
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from analyze_donations import summarize_donations
from analyze_inventory import summarize_inventory
from analyze_sales import summarize_sales, summarize_team_contribution
from clean_data import run_cleaning
from model_utils import PRICE_FEATURES, load_price_model_data
from utils import DATA_PROCESSED_DIR, filter_confirmed_donations


EXPECTED_TEAMS = {"Team A", "Team B", "Team C", "Team D"}
EXPECTED_BOOTHS = {"Booth A", "Booth B", "Booth C", "Booth D", "Shared Table"}
EXPECTED_CATEGORIES = {
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


class AnalysisTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        run_cleaning()
        cls.donations = pd.read_csv(DATA_PROCESSED_DIR / "cleaned_donations.csv")
        cls.inventory = pd.read_csv(DATA_PROCESSED_DIR / "cleaned_inventory.csv")
        cls.sales = pd.read_csv(DATA_PROCESSED_DIR / "cleaned_sales.csv")
        cls.merged = pd.read_csv(DATA_PROCESSED_DIR / "merged_event_data.csv")

    def test_donation_summary_matches_confirmed_records(self):
        donor_type_summary, team_summary, total_direct_donations, average_donation = (
            summarize_donations(self.donations)
        )
        confirmed = filter_confirmed_donations(self.donations)

        self.assertGreater(total_direct_donations, 0)
        self.assertAlmostEqual(total_direct_donations, confirmed["donation_amount_cny"].sum())
        self.assertAlmostEqual(average_donation, confirmed["donation_amount_cny"].mean())
        self.assertAlmostEqual(
            donor_type_summary["total_donation_cny"].sum(),
            total_direct_donations,
        )
        self.assertAlmostEqual(
            team_summary["team_donation_cny"].sum(),
            total_direct_donations,
        )

    def test_inventory_summary_matches_inventory_records(self):
        category_summary, status_summary, team_inventory_summary = summarize_inventory(
            self.inventory
        )

        self.assertEqual(category_summary["total_quantity"].sum(), self.inventory["quantity"].sum())
        self.assertEqual(status_summary["total_quantity"].sum(), self.inventory["quantity"].sum())
        self.assertEqual(
            team_inventory_summary["total_quantity"].sum(),
            self.inventory["quantity"].sum(),
        )
        self.assertTrue(set(category_summary["item_category"]).issubset(EXPECTED_CATEGORIES))

    def test_sales_summary_matches_sale_records(self):
        revenue_by_category, revenue_by_booth, revenue_by_team, estimate_vs_actual = (
            summarize_sales(self.sales, self.merged)
        )
        total_sale_revenue = self.sales["total_sale_cny"].sum()

        self.assertGreater(total_sale_revenue, 0)
        self.assertAlmostEqual(revenue_by_category["sale_revenue_cny"].sum(), total_sale_revenue)
        self.assertAlmostEqual(revenue_by_booth["sale_revenue_cny"].sum(), total_sale_revenue)
        self.assertAlmostEqual(revenue_by_team["sale_revenue_cny"].sum(), total_sale_revenue)
        self.assertAlmostEqual(
            estimate_vs_actual["actual_sale_total_cny"].sum(),
            total_sale_revenue,
        )

    def test_total_funds_raised_is_over_26000(self):
        confirmed = filter_confirmed_donations(self.donations)
        total_donations = confirmed["donation_amount_cny"].sum()
        total_sales = self.sales["total_sale_cny"].sum()

        self.assertGreater(total_donations, 21000)
        self.assertLess(total_donations, 23000)
        self.assertGreater(total_sales, 4000)
        self.assertLess(total_sales, 6000)
        self.assertGreater(total_donations + total_sales, 26000)

    def test_sale_totals_match_quantity_times_price(self):
        expected_total = self.sales["quantity_sold"] * self.sales["final_unit_price_cny"]
        self.assertTrue(
            (self.sales["total_sale_cny"].round(2) == expected_total.round(2)).all()
        )

    def test_sale_records_match_inventory_fields(self):
        inventory_lookup = self.inventory[
            ["item_id", "item_category", "booth_area", "team", "quantity"]
        ].rename(
            columns={
                "item_category": "inventory_category",
                "booth_area": "inventory_booth_area",
                "team": "inventory_team",
                "quantity": "inventory_quantity",
            }
        )
        sales_with_inventory = self.sales.merge(inventory_lookup, on="item_id", how="left")

        self.assertFalse(sales_with_inventory["inventory_category"].isna().any())
        self.assertTrue(
            (
                sales_with_inventory["item_category"]
                == sales_with_inventory["inventory_category"]
            ).all()
        )
        self.assertTrue(
            (
                sales_with_inventory["booth_area"]
                == sales_with_inventory["inventory_booth_area"]
            ).all()
        )
        self.assertTrue(
            (sales_with_inventory["team"] == sales_with_inventory["inventory_team"]).all()
        )

    def test_sold_quantity_does_not_exceed_inventory_quantity(self):
        sold_by_item = (
            self.sales.groupby("item_id", as_index=False)
            .agg(total_quantity_sold=("quantity_sold", "sum"))
            .merge(self.inventory[["item_id", "quantity"]], on="item_id", how="left")
        )
        self.assertTrue(
            (sold_by_item["total_quantity_sold"] <= sold_by_item["quantity"]).all()
        )

    def test_standardized_names(self):
        self.assertTrue(set(self.donations["team"]).issubset(EXPECTED_TEAMS))
        self.assertTrue(set(self.inventory["team"]).issubset(EXPECTED_TEAMS))
        self.assertTrue(set(self.sales["team"]).issubset(EXPECTED_TEAMS))
        self.assertTrue(set(self.inventory["booth_area"]).issubset(EXPECTED_BOOTHS))
        self.assertTrue(set(self.sales["booth_area"]).issubset(EXPECTED_BOOTHS))
        self.assertTrue(set(self.inventory["item_category"]).issubset(EXPECTED_CATEGORIES))
        self.assertTrue(set(self.sales["item_category"]).issubset(EXPECTED_CATEGORIES))

    def test_team_contribution_summary_matches_inputs(self):
        _, _, revenue_by_team, _ = summarize_sales(self.sales, self.merged)
        team_summary = summarize_team_contribution(self.donations, revenue_by_team)
        confirmed = filter_confirmed_donations(self.donations)

        expected_total = confirmed["donation_amount_cny"].sum() + self.sales[
            "total_sale_cny"
        ].sum()
        self.assertAlmostEqual(
            team_summary["total_contribution_cny"].sum(),
            expected_total,
        )
        self.assertEqual(team_summary["team_rank"].min(), 1)

    def test_price_model_uses_pre_sale_features(self):
        self.assertIn("quantity", PRICE_FEATURES)
        self.assertNotIn("quantity_sold", PRICE_FEATURES)
        self.assertNotIn("total_sale_cny", PRICE_FEATURES)
        self.assertNotIn("actual_sale_total_cny", PRICE_FEATURES)

    def test_price_model_features_match_inventory_records(self):
        model_data = load_price_model_data()
        inventory_lookup = self.inventory[
            [
                "item_id",
                "item_category",
                "booth_area",
                "team",
                "condition",
                "estimated_unit_value_cny",
                "quantity",
            ]
        ]
        checked = model_data.merge(
            inventory_lookup,
            on="item_id",
            suffixes=("_model", "_inventory"),
        )

        for column in PRICE_FEATURES:
            self.assertTrue(
                (checked[f"{column}_model"] == checked[f"{column}_inventory"]).all(),
                f"{column} should come from inventory records.",
            )


if __name__ == "__main__":
    unittest.main()
