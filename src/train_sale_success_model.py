import os

os.environ.setdefault("MPLCONFIGDIR", ".matplotlib_cache")

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier

from model_utils import (
    CHARTS_DIR,
    SALE_SUCCESS_NUMERIC_FEATURES,
    build_model_pipeline,
    evaluate_classification_model,
    load_metrics,
    load_sale_success_model_data,
    split_classification_data,
    update_metrics,
    write_model_report,
)
from utils import ensure_directory


def train_sale_success_models():
    model_data = load_sale_success_model_data()
    x_train, x_test, y_train, y_test = split_classification_data(model_data)

    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000),
        "Decision Tree Classifier": DecisionTreeClassifier(
            random_state=42,
            max_depth=4,
            min_samples_leaf=2,
        ),
    }

    results = {}
    predictions = {}

    for model_name, model in models.items():
        pipeline = build_model_pipeline(model, SALE_SUCCESS_NUMERIC_FEATURES)
        pipeline.fit(x_train, y_train)
        model_metrics, y_pred = evaluate_classification_model(pipeline, x_test, y_test)
        results[model_name] = model_metrics
        predictions[model_name] = y_pred

    results["class_balance"] = {
        "sold_success_count": int(model_data["sold_success"].sum()),
        "not_sold_count": int((model_data["sold_success"] == 0).sum()),
    }

    best_model_name = max(
        [name for name in results if name != "class_balance"],
        key=lambda name: results[name]["accuracy"],
    )
    create_confusion_matrix_chart(
        results[best_model_name]["confusion_matrix"],
        best_model_name,
    )
    create_model_comparison_chart(results)

    metrics = update_metrics("sale_success_classification", results)
    write_model_report(metrics)

    print("Sale success model training finished.")
    for model_name, model_metrics in results.items():
        if model_name == "class_balance":
            continue
        print(
            f"{model_name}: accuracy={model_metrics['accuracy']}, "
            f"precision={model_metrics['precision']}, recall={model_metrics['recall']}"
        )


def create_confusion_matrix_chart(matrix, model_name):
    ensure_directory(CHARTS_DIR)
    plt.figure(figsize=(5, 4))
    plt.imshow(matrix, cmap="Blues")
    plt.title(f"Sale Success Confusion Matrix ({model_name})")
    plt.xticks([0, 1], ["Not sold", "Sold"])
    plt.yticks([0, 1], ["Not sold", "Sold"])
    plt.xlabel("Predicted")
    plt.ylabel("Actual")

    for row_index, row in enumerate(matrix):
        for column_index, value in enumerate(row):
            plt.text(column_index, row_index, str(value), ha="center", va="center")

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "sale_success_confusion_matrix.png", dpi=160)
    plt.close()


def create_model_comparison_chart(classification_results):
    metrics = load_metrics()
    price_results = metrics.get("price_prediction", {})
    regression_labels = list(price_results.keys())
    regression_mae = [price_results[name]["mae"] for name in regression_labels]

    classifier_labels = [
        name for name in classification_results.keys() if name != "class_balance"
    ]
    classifier_accuracy = [
        classification_results[name]["accuracy"] for name in classifier_labels
    ]

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))

    axes[0].bar(regression_labels, regression_mae, color="#4C78A8")
    axes[0].set_title("Price Model MAE")
    axes[0].set_ylabel("MAE (CNY)")
    axes[0].tick_params(axis="x", rotation=20)

    axes[1].bar(classifier_labels, classifier_accuracy, color="#F28E2B")
    axes[1].set_title("Sale Success Model Accuracy")
    axes[1].set_ylabel("Accuracy")
    axes[1].set_ylim(0, 1)
    axes[1].tick_params(axis="x", rotation=20)

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "model_comparison.png", dpi=160)
    plt.close()


if __name__ == "__main__":
    train_sale_success_models()
