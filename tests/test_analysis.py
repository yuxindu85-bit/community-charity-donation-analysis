import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from clean_data import main as clean_data_main
from analyze_charity_sale import (
    calculate_total_donations,
    calculate_total_funds_raised,
    calculate_total_sale_revenue,
    create_category_summary,
    create_team_summary,
    load_cleaned_data,
)


class CharitySaleAnalysisTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        clean_data_main()
        cls.data = load_cleaned_data()

    def test_total_donation_calculation(self) -> None:
        self.assertEqual(calculate_total_donations(self.data), 23090)

    def test_total_sale_revenue_calculation(self) -> None:
        self.assertEqual(calculate_total_sale_revenue(self.data), 4821)

    def test_category_summary_calculation(self) -> None:
        category_summary = create_category_summary(self.data)
        handmade_row = category_summary[
            category_summary["item_category"] == "Handmade Crafts"
        ].iloc[0]
        self.assertEqual(handmade_row["sale_revenue"], 990)
        self.assertEqual(handmade_row["items_sold"], 91)

    def test_team_summary_calculation(self) -> None:
        team_summary = create_team_summary(self.data)
        team_a_row = team_summary[team_summary["team"] == "Team A"].iloc[0]
        self.assertEqual(team_a_row["direct_donations"], 7700)
        self.assertEqual(team_a_row["sale_revenue"], 1430)
        self.assertEqual(team_a_row["total_contribution"], 9130)

    def test_total_funds_raised_is_over_26000(self) -> None:
        self.assertGreater(calculate_total_funds_raised(self.data), 26000)


if __name__ == "__main__":
    unittest.main()
