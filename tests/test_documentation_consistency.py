import json
import sys
import unittest
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from utils import DATA_PROCESSED_DIR, filter_confirmed_donations, format_currency


class DocumentationConsistencyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.readme_text = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
        cls.final_report_text = (
            PROJECT_ROOT / "reports" / "final_charity_sale_report.md"
        ).read_text(encoding="utf-8")
        cls.model_report_text = (
            PROJECT_ROOT / "reports" / "model_report.md"
        ).read_text(encoding="utf-8")
        cls.metrics = json.loads(
            (PROJECT_ROOT / "models" / "model_metrics.json").read_text(
                encoding="utf-8"
            )
        )

        donations = pd.read_csv(DATA_PROCESSED_DIR / "cleaned_donations.csv")
        sales = pd.read_csv(DATA_PROCESSED_DIR / "cleaned_sales.csv")
        confirmed_donations = filter_confirmed_donations(donations)

        cls.total_direct_donations = confirmed_donations["donation_amount_cny"].sum()
        cls.total_sale_revenue = sales["total_sale_cny"].sum()
        cls.total_funds = cls.total_direct_donations + cls.total_sale_revenue

    def test_readme_totals_match_processed_data(self):
        expected_values = [
            format_currency(self.total_direct_donations),
            format_currency(self.total_sale_revenue),
            format_currency(self.total_funds),
        ]

        for expected_value in expected_values:
            self.assertIn(expected_value, self.readme_text)

    def test_final_report_totals_match_processed_data(self):
        expected_values = [
            format_currency(self.total_direct_donations),
            format_currency(self.total_sale_revenue),
            format_currency(self.total_funds),
        ]

        for expected_value in expected_values:
            self.assertIn(expected_value, self.final_report_text)

    def test_readme_model_metrics_match_json_output(self):
        price_metrics = self.metrics["price_prediction"]
        sale_metrics = self.metrics["sale_success_classification"]

        for model_name, model_values in price_metrics.items():
            self.assertIn(model_name, self.readme_text)
            self.assertIn(f"MAE {model_values['mae']:.3f}", self.readme_text)
            self.assertIn(f"RMSE {model_values['rmse']:.3f}", self.readme_text)
            self.assertIn(f"R2 {model_values['r2_score']:.3f}", self.readme_text)

        for model_name, model_values in sale_metrics.items():
            if model_name == "class_balance":
                continue
            self.assertIn(model_name, self.readme_text)
            self.assertIn(f"accuracy {model_values['accuracy']:.3f}", self.readme_text)
            self.assertIn(f"precision {model_values['precision']:.3f}", self.readme_text)
            self.assertIn(f"recall {model_values['recall']:.3f}", self.readme_text)

    def test_model_report_mentions_small_dataset_limits(self):
        limitation_phrases = [
            "small and anonymized",
            "not official decision-making",
            "high accuracy should not be over-interpreted",
        ]

        for phrase in limitation_phrases:
            self.assertIn(phrase, self.model_report_text)


if __name__ == "__main__":
    unittest.main()
