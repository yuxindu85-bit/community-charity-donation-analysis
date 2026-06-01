import json
import re
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
from model_utils import METRICS_PATH, MODEL_REPORT_PATH
from train_price_model import train_price_models
from train_sale_success_model import train_sale_success_models
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
            "predicted_vs_actual_price.png",
            "feature_importance_price.png",
            "sale_success_confusion_matrix.png",
            "model_comparison.png",
        ]
        for file_name in expected_charts:
            file_path = CHARTS_DIR / file_name
            self.assertTrue(file_path.exists())
            self.assertGreater(file_path.stat().st_size, 0)

    def test_model_and_report_outputs_are_created(self):
        expected_files = [
            METRICS_PATH,
            PROJECT_ROOT / "reports" / "final_charity_sale_report.md",
            PROJECT_ROOT / "reports" / "event_operation_review.md",
            MODEL_REPORT_PATH,
            PROJECT_ROOT / "reports" / "llm_operation_review.md",
            PROJECT_ROOT / "docs" / "llm_usage.md",
            PROJECT_ROOT / "notebooks" / "charity_sale_analysis_walkthrough.ipynb",
            PROJECT_ROOT / "notebooks" / "charity_sale_analysis_walkthrough.md",
            PROJECT_ROOT / "dashboard" / "app.py",
        ]
        for file_path in expected_files:
            self.assertTrue(file_path.exists())
            self.assertGreater(file_path.stat().st_size, 0)

    def test_readme_image_links_point_to_existing_files(self):
        readme_text = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
        image_links = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", readme_text)
        local_image_links = [
            link
            for link in image_links
            if not link.startswith(("http://", "https://"))
        ]

        self.assertGreater(len(local_image_links), 0)
        for link in local_image_links:
            self.assertTrue(
                (PROJECT_ROOT / link).exists(),
                f"README image link does not exist: {link}",
            )

    def test_github_actions_workflow_exists(self):
        workflow_path = PROJECT_ROOT / ".github" / "workflows" / "tests.yml"
        self.assertTrue(workflow_path.exists())
        workflow_text = workflow_path.read_text(encoding="utf-8")
        self.assertIn("python src/run_all.py", workflow_text)
        self.assertIn("python -m unittest discover -s tests", workflow_text)
        self.assertIn("python -m compileall src tests dashboard tools", workflow_text)
        self.assertIn("python -m py_compile dashboard/app.py", workflow_text)

    def test_notebook_has_no_saved_error_outputs(self):
        notebook_path = (
            PROJECT_ROOT / "notebooks" / "charity_sale_analysis_walkthrough.ipynb"
        )
        notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
        cells = notebook.get("cells", [])

        self.assertGreater(len(cells), 0)
        self.assertTrue(any(cell.get("cell_type") == "markdown" for cell in cells))
        self.assertTrue(any(cell.get("cell_type") == "code" for cell in cells))

        for cell in cells:
            for output in cell.get("outputs", []):
                self.assertNotEqual(output.get("output_type"), "error")


if __name__ == "__main__":
    unittest.main()
