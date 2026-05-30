import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from analyze_booth_layout import run_analysis as run_booth_analysis
from analyze_donations import run_analysis as run_donation_analysis
from analyze_inventory import run_analysis as run_inventory_analysis
from analyze_sales import run_analysis as run_sales_analysis
from clean_data import run_cleaning
from create_charts import create_all_charts
from utils import CHARTS_DIR, SUMMARY_DIR


class OutputTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        run_cleaning()
        run_donation_analysis()
        run_inventory_analysis()
        run_sales_analysis()
        run_booth_analysis()
        create_all_charts()

    def test_summary_tables_are_created(self):
        expected_tables = [
            "donation_summary.csv",
            "category_summary.csv",
            "team_summary.csv",
            "booth_summary.csv",
            "estimate_vs_actual_summary.csv",
        ]
        for file_name in expected_tables:
            file_path = SUMMARY_DIR / file_name
            self.assertTrue(file_path.exists())
            self.assertGreater(file_path.stat().st_size, 0)

    def test_chart_files_are_created(self):
        expected_charts = [
            "revenue_by_category.png",
            "item_quantity_by_category.png",
            "team_contribution.png",
            "estimate_vs_actual_price.png",
            "booth_revenue_comparison.png",
            "donation_source_breakdown.png",
        ]
        for file_name in expected_charts:
            file_path = CHARTS_DIR / file_name
            self.assertTrue(file_path.exists())
            self.assertGreater(file_path.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
