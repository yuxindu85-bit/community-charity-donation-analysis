import json
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from clean_data import run_cleaning
from model_utils import METRICS_PATH, MODEL_REPORT_PATH, CHARTS_DIR
from train_price_model import train_price_models
from train_sale_success_model import train_sale_success_models


class ModelOutputTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        run_cleaning()
        train_price_models()
        train_sale_success_models()

    def test_model_metrics_file_is_created(self):
        self.assertTrue(METRICS_PATH.exists())
        metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
        self.assertIn("price_prediction", metrics)
        self.assertIn("sale_success_classification", metrics)

    def test_price_model_metrics_exist(self):
        metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
        price_metrics = metrics["price_prediction"]
        self.assertIn("Linear Regression", price_metrics)
        self.assertIn("Random Forest Regressor", price_metrics)
        self.assertIn("mae", price_metrics["Linear Regression"])

    def test_sale_success_metrics_exist(self):
        metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
        sale_metrics = metrics["sale_success_classification"]
        self.assertIn("Logistic Regression", sale_metrics)
        self.assertIn("Decision Tree Classifier", sale_metrics)
        self.assertIn("confusion_matrix", sale_metrics["Decision Tree Classifier"])

    def test_model_report_and_charts_exist(self):
        expected_charts = [
            "predicted_vs_actual_price.png",
            "feature_importance_price.png",
            "sale_success_confusion_matrix.png",
            "model_comparison.png",
        ]
        self.assertTrue(MODEL_REPORT_PATH.exists())
        for file_name in expected_charts:
            file_path = CHARTS_DIR / file_name
            self.assertTrue(file_path.exists())
            self.assertGreater(file_path.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
