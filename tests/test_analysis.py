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
from utils import DATA_PROCESSED_DIR


class AnalysisTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        run_cleaning()
        cls.donations = pd.read_csv(DATA_PROCESSED_DIR / "cleaned_donations.csv")
        cls.inventory = pd.read_csv(DATA_PROCESSED_DIR / "cleaned_inventory.csv")
        cls.sales = pd.read_csv(DATA_PROCESSED_DIR / "cleaned_sales.csv")
        cls.merged = pd.read_csv(DATA_PROCESSED_DIR / "merged_event_data.csv")

    def test_donation_total_is_correct(self):
        _, _, total_direct_donations, average_donation = summarize_donations(
            self.donations
        )
        self.assertEqual(total_direct_donations, 22190)
        self.assertAlmostEqual(average_donation, 1305.29, places=2)

    def test_sale_total_is_correct(self):
        total_sale_revenue = self.sales["total_sale_cny"].sum()
        self.assertEqual(total_sale_revenue, 5269)

    def test_total_funds_raised_is_over_26000(self):
        total_donations = self.donations["donation_amount_cny"].sum()
        total_sales = self.sales["total_sale_cny"].sum()
        self.assertEqual(total_donations + total_sales, 27459)
        self.assertGreater(total_donations + total_sales, 26000)

    def test_inventory_category_summary(self):
        category_summary, _, _ = summarize_inventory(self.inventory)
        snack_row = category_summary[
            category_summary["item_category"] == "Snacks"
        ].iloc[0]
        self.assertEqual(snack_row["total_quantity"], 150)

    def test_estimate_vs_actual_summary(self):
        _, _, revenue_by_team, estimate_vs_actual = summarize_sales(self.sales, self.merged)
        crafts_row = estimate_vs_actual[
            estimate_vs_actual["item_category"] == "Handmade Crafts"
        ].iloc[0]
        self.assertEqual(crafts_row["actual_sale_total_cny"], 890)

        team_summary = summarize_team_contribution(self.donations, revenue_by_team)
        top_team = team_summary.iloc[0]
        self.assertEqual(top_team["team"], "Team B")
        self.assertEqual(top_team["team_rank"], 1)


if __name__ == "__main__":
    unittest.main()
