import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from analyze_charity_sale import (
    calculate_totals,
    load_data,
    make_summaries,
)


class CharitySaleAnalysisTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.donations, cls.sales = load_data()
        cls.donor_type_summary, cls.category_summary, cls.team_summary, _ = make_summaries(
            cls.donations, cls.sales
        )
        cls.totals = calculate_totals(cls.donations, cls.sales)

    def test_total_donation_calculation(self):
        self.assertEqual(self.totals["total_direct_donations"], 23090)

    def test_total_sale_revenue_calculation(self):
        self.assertEqual(self.totals["total_sale_revenue"], 4821)

    def test_total_funds_raised_is_over_26000(self):
        self.assertGreater(self.totals["total_funds_raised"], 26000)

    def test_category_summary_calculation(self):
        handmade_row = self.category_summary[
            self.category_summary["item_category"] == "Handmade Crafts"
          ].iloc[0]
        self.assertEqual(handmade_row["sale_revenue_cny"], 990)
        self.assertEqual(handmade_row["items_sold"], 91)

    def test_team_summary_calculation(self):
        team_a_row = self.team_summary[self.team_summary["team"] == "Team A"].iloc[0]
        self.assertEqual(team_a_row["direct_donation_cny"], 7700)
        self.assertEqual(team_a_row["sale_revenue_cny"], 1430)
        self.assertEqual(team_a_row["total_contribution_cny"], 9130)


if __name__ == "__main__":
    unittest.main()
