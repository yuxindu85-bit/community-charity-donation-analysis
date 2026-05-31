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
from train_price_model import train_price_models
from train_sale_success_model import train_sale_success_models


class OutputTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        run_cleaning()
        run_donation_analysis()
        run_inventory_analysis()
        run_sales_analysis()
        run_booth_analysis()
        create_all_charts()
        train_price_models()
        train_sale_success_models()

    def test_summary_tables_are_created(self):
        expected_tables = [
            "donation_summary.csv",
            "donation_by_team.csv",
            "category_summary.csv",
            "inventory_status_summary.csv",
            "sales_by_category.csv",
            "sales_by_team.csv",
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

    def test_model_and_report_outputs_are_created(self):
        expected_files = [
            PROJECT_ROOT / "models" / "model_metrics.json",
            PROJECT_ROOT / "reports" / "final_charity_sale_report.md",
            PROJECT_ROOT / "reports" / "event_operation_review.md",
            PROJECT_ROOT / "reports" / "model_report.md",
            PROJECT_ROOT / "notebooks" / "charity_sale_analysis_walkthrough.ipynb",
            PROJECT_ROOT / "dashboard" / "app.py",
        ]
        for file_path in expected_files:
            self.assertTrue(file_path.exists())
            self.assertGreater(file_path.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
