import os

os.environ.setdefault("MPLCONFIGDIR", ".matplotlib_cache")

import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression

from model_utils import (
    CHARTS_DIR,
    build_model_pipeline,
    get_feature_names,
    load_price_model_data,
    regression_metrics,
    split_regression_data,
    update_metrics,
    write_model_report,
)
from utils import ensure_directory


def train_price_models():
    model_data = load_price_model_data()
    x_train, x_test, y_train, y_test = split_regression_data(model_data)

    models = {
        "Linear Regression": LinearRegression(),
        "Random Forest Regressor": RandomForestRegressor(
            n_estimators=80,
            random_state=42,
            min_samples_leaf=2,
        ),
    }

    results = {}
    trained_models = {}
    predictions = {}

    for model_name, model in models.items():
        pipeline = build_model_pipeline(model)
        pipeline.fit(x_train, y_train)
        y_pred = pipeline.predict(x_test)
        results[model_name] = regression_metrics(y_test, y_pred)
        trained_models[model_name] = pipeline
        predictions[model_name] = y_pred

    best_model_name = min(results, key=lambda name: results[name]["mae"])
    create_predicted_vs_actual_chart(y_test, predictions[best_model_name], best_model_name)
    create_feature_importance_chart(trained_models["Random Forest Regressor"])

    metrics = update_metrics("price_prediction", results)
    write_model_report(metrics)

    print("Price prediction model training finished.")
    for model_name, model_metrics in results.items():
        print(
            f"{model_name}: MAE={model_metrics['mae']}, "
            f"RMSE={model_metrics['rmse']}, R2={model_metrics['r2_score']}"
        )


def create_predicted_vs_actual_chart(y_true, y_pred, model_name):
    ensure_directory(CHARTS_DIR)
    plt.figure(figsize=(7, 6))
    plt.scatter(y_true, y_pred, color="#4C78A8", alpha=0.8)
    min_value = min(y_true.min(), y_pred.min())
    max_value = max(y_true.max(), y_pred.max())
    plt.plot([min_value, max_value], [min_value, max_value], color="#E15759")
    plt.title(f"Predicted vs Actual Final Sale Price ({model_name})")
    plt.xlabel("Actual final unit price (CNY)")
    plt.ylabel("Predicted final unit price (CNY)")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "predicted_vs_actual_price.png", dpi=160)
    plt.close()


def create_feature_importance_chart(random_forest_pipeline):
    feature_names = get_feature_names(random_forest_pipeline)
    importances = random_forest_pipeline.named_steps["model"].feature_importances_
    sorted_pairs = sorted(
        zip(feature_names, importances),
        key=lambda pair: pair[1],
        reverse=True,
    )[:10]
    labels = [pair[0] for pair in sorted_pairs]
    values = [pair[1] for pair in sorted_pairs]

    plt.figure(figsize=(9, 5))
    plt.barh(labels[::-1], values[::-1], color="#59A14F")
    plt.title("Top Price Model Feature Importances")
    plt.xlabel("Importance")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "feature_importance_price.png", dpi=160)
    plt.close()


if __name__ == "__main__":
    train_price_models()
