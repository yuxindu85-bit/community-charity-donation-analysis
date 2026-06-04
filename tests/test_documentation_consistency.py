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

    def test_readme_model_section_matches_model_output_structure(self):
        price_metrics = self.metrics["price_prediction"]
        sale_metrics = self.metrics["sale_success_classification"]

        for model_name, model_values in price_metrics.items():
            self.assertIn(model_name, self.readme_text)
            metric_keys = {key.lower() for key in model_values}
            self.assertIn("mae", metric_keys)
            self.assertIn("rmse", metric_keys)
            self.assertIn("r2_score", metric_keys)

        for model_name, model_values in sale_metrics.items():
            if model_name == "class_balance":
                continue
            self.assertIn(model_name, self.readme_text)
            self.assertIn("accuracy", model_values)
            self.assertIn("precision", model_values)
            self.assertIn("recall", model_values)

        model_limit_phrases = [
            "exploratory",
            "small",
            "not official",
            "high model scores may reflect simple patterns",
        ]
        normalized_readme_text = " ".join(self.readme_text.lower().split())
        for phrase in model_limit_phrases:
            self.assertIn(phrase, normalized_readme_text)

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
