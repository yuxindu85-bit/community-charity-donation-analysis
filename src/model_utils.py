import json
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from utils import CHARTS_DIR, DATA_PROCESSED_DIR, PROJECT_ROOT, ensure_directory, load_csv


MODELS_DIR = PROJECT_ROOT / "models"
METRICS_PATH = MODELS_DIR / "model_metrics.json"
MODEL_REPORT_PATH = PROJECT_ROOT / "reports" / "model_report.md"

PRICE_FEATURES = [
    "item_category",
    "condition",
    "estimated_unit_value_cny",
    "booth_area",
    "team",
    "quantity",
]

SALE_SUCCESS_FEATURES = [
    "item_category",
    "condition",
    "estimated_unit_value_cny",
    "booth_area",
    "team",
    "quantity",
]

CATEGORICAL_FEATURES = ["item_category", "condition", "booth_area", "team"]
PRICE_NUMERIC_FEATURES = ["estimated_unit_value_cny", "quantity"]
SALE_SUCCESS_NUMERIC_FEATURES = ["estimated_unit_value_cny", "quantity"]


def load_price_model_data():
    inventory = load_csv(DATA_PROCESSED_DIR / "cleaned_inventory.csv")
    sales = load_csv(DATA_PROCESSED_DIR / "cleaned_sales.csv")

    item_sale_summary = (
        sales.groupby("item_id", as_index=False)
        .agg(
            quantity_sold=("quantity_sold", "sum"),
            total_sale_cny=("total_sale_cny", "sum"),
        )
    )
    item_sale_summary["final_unit_price_cny"] = (
        item_sale_summary["total_sale_cny"] / item_sale_summary["quantity_sold"]
    )

    model_data = item_sale_summary.merge(
        inventory[
            [
                "item_id",
                "item_category",
                "booth_area",
                "team",
                "condition",
                "estimated_unit_value_cny",
                "quantity",
            ]
        ],
        on="item_id",
        how="left",
    )
    return model_data.dropna(subset=PRICE_FEATURES + ["final_unit_price_cny"])


def load_sale_success_model_data():
    merged_event_data = load_csv(DATA_PROCESSED_DIR / "merged_event_data.csv")
    merged_event_data["sold_success"] = (merged_event_data["quantity_sold"] > 0).astype(int)
    return merged_event_data.dropna(subset=SALE_SUCCESS_FEATURES + ["sold_success"])


def prepare_features(dataframe, feature_columns, target_column):
    return dataframe[feature_columns], dataframe[target_column]


def build_preprocessor(numeric_features):
    return ColumnTransformer(
        transformers=[
            ("category", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
            ("number", "passthrough", numeric_features),
        ]
    )


def build_model_pipeline(model, numeric_features=None):
    if numeric_features is None:
        numeric_features = SALE_SUCCESS_NUMERIC_FEATURES
    return Pipeline(
        steps=[
            ("preprocess", build_preprocessor(numeric_features)),
            ("model", model),
        ]
    )


def train_test_split_data(x_values, y_values, stratify=None):
    return train_test_split(
        x_values,
        y_values,
        test_size=0.3,
        random_state=42,
        stratify=stratify,
    )


def split_regression_data(dataframe):
    x_values, y_values = prepare_features(
        dataframe,
        PRICE_FEATURES,
        "final_unit_price_cny",
    )
    return train_test_split_data(x_values, y_values)


def split_classification_data(dataframe):
    x_values, y_values = prepare_features(dataframe, SALE_SUCCESS_FEATURES, "sold_success")
    return train_test_split_data(x_values, y_values, stratify=y_values)


def regression_metrics(y_true, y_pred):
    mse = mean_squared_error(y_true, y_pred)
    return {
        "mae": round(float(mean_absolute_error(y_true, y_pred)), 3),
        "rmse": round(float(mse**0.5), 3),
        "r2_score": round(float(r2_score(y_true, y_pred)), 3),
    }


def evaluate_regression_model(model, x_test, y_test):
    y_pred = model.predict(x_test)
    return regression_metrics(y_test, y_pred), y_pred


def classification_metrics(y_true, y_pred):
    return {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 3),
        "precision": round(
            float(precision_score(y_true, y_pred, zero_division=0)),
            3,
        ),
        "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 3),
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=[0, 1]).tolist(),
    }


def evaluate_classification_model(model, x_test, y_test):
    y_pred = model.predict(x_test)
    return classification_metrics(y_test, y_pred), y_pred


def get_feature_names(pipeline):
    preprocessor = pipeline.named_steps["preprocess"]
    category_names = preprocessor.named_transformers_["category"].get_feature_names_out(
        CATEGORICAL_FEATURES
    )
    numeric_features = list(preprocessor.transformers_[1][2])
    return list(category_names) + numeric_features


def load_metrics(path=METRICS_PATH):
    path = Path(path)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_metrics(metrics, path=METRICS_PATH):
    path = Path(path)
    ensure_directory(path.parent)
    path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")


def update_metrics(section, values):
    metrics = load_metrics()
    metrics[section] = values
    save_metrics(metrics)
    return metrics


def write_model_report(metrics):
    ensure_directory(MODEL_REPORT_PATH.parent)
    ensure_directory(CHARTS_DIR)

    price_metrics = metrics.get("price_prediction", {})
    sale_metrics = metrics.get("sale_success_classification", {})

    report = [
        "# Simple Machine Learning Model Report",
        "",
        "## Purpose",
        "",
        "This report summarizes two beginner-friendly machine learning experiments for the charity sale project. The models are exploratory learning tools, not official financial or operational prediction systems.",
        "",
        "## Features Used",
        "",
        "- Item category",
        "- Item condition",
        "- Estimated unit value",
        "- Booth area",
        "- Team",
        "- Donated quantity",
        "",
        "## Price Prediction Regression Model",
        "",
        "Goal: predict final item sale price using item category, condition, estimated value, booth area, team, and donated quantity.",
        "The input features come from the inventory table. Sale records are used only to calculate the target final unit price for sold items.",
        "",
        "| Model | MAE | RMSE | R2 score |",
        "| --- | ---: | ---: | ---: |",
    ]

    for model_name, model_values in price_metrics.items():
        report.append(
            f"| {model_name} | {model_values['mae']} | {model_values['rmse']} | {model_values['r2_score']} |"
        )

    report.extend(
        [
            "",
            "## Sale Success Classification Model",
            "",
            "Goal: predict whether an item group is likely to sell based on category, condition, estimated value, booth area, team, and quantity.",
        ]
    )

    class_balance = sale_metrics.get("class_balance", {})
    if class_balance:
        report.extend(
            [
                "",
                f"Class balance: {class_balance.get('sold_success_count', 0)} sold or partially sold item groups and {class_balance.get('not_sold_count', 0)} unsold item groups.",
                "",
            ]
        )

    report.extend(
        [
            "| Model | Accuracy | Precision | Recall |",
            "| --- | ---: | ---: | ---: |",
        ]
    )

    for model_name, model_values in sale_metrics.items():
        if model_name == "class_balance":
            continue
        report.append(
            f"| {model_name} | {model_values['accuracy']} | {model_values['precision']} | {model_values['recall']} |"
        )

    report.extend(
        [
            "",
            "## Visualizations",
            "",
            "- `reports/charts/predicted_vs_actual_price.png`",
            "- `reports/charts/feature_importance_price.png`",
            "- `reports/charts/sale_success_confusion_matrix.png`",
            "- `reports/charts/model_comparison.png`",
            "",
            "## Limitations",
            "",
            "- The dataset is small and anonymized.",
            "- The sale success dataset is imbalanced, so high accuracy should not be over-interpreted.",
            "- The models are useful for learning and reflection, not official decision-making.",
            "- Some sale outcomes may depend on booth traffic, buyer interest, weather, and timing, which were not fully recorded.",
            "- Model results can change if more complete future event data is added.",
            "",
            "## What I Learned",
            "",
            "The models helped me practice connecting real event records with basic machine learning. I also learned that model results can look strong on a small dataset, so they need to be explained carefully.",
        ]
    )

    MODEL_REPORT_PATH.write_text("\n".join(report) + "\n", encoding="utf-8")
