# Simple Machine Learning Model Report

## Purpose

This report summarizes two beginner-friendly machine learning experiments for the charity sale project. The models are exploratory learning tools, not official financial or operational prediction systems.

## Features Used

- Item category
- Item condition
- Estimated unit value
- Booth area
- Team
- Donated quantity

## Price Prediction Regression Model

Goal: predict final item sale price using item category, condition, estimated value, booth area, team, and donated quantity.
The input features come from the inventory table. Sale records are used only to calculate the target final unit price for sold items.

| Model | MAE | RMSE | R2 score |
| --- | ---: | ---: | ---: |
| Linear Regression | 1.622 | 2.128 | 0.987 |
| Random Forest Regressor | 2.747 | 4.53 | 0.943 |

## Sale Success Classification Model

Goal: predict whether an item group is likely to sell based on category, condition, estimated value, booth area, team, and quantity.

Class balance: 27 sold or partially sold item groups and 4 unsold item groups.

| Model | Accuracy | Precision | Recall |
| --- | ---: | ---: | ---: |
| Logistic Regression | 1.0 | 1.0 | 1.0 |
| Decision Tree Classifier | 0.8 | 1.0 | 0.778 |

## Visualizations

- `reports/charts/predicted_vs_actual_price.png`
- `reports/charts/feature_importance_price.png`
- `reports/charts/sale_success_confusion_matrix.png`
- `reports/charts/model_comparison.png`

## Limitations

- The dataset is small and anonymized.
- The sale success dataset is imbalanced, so high accuracy should not be over-interpreted.
- The models are useful for learning and reflection, not official decision-making.
- Some sale outcomes may depend on booth traffic, buyer interest, weather, and timing, which were not fully recorded.
- Model results can change if more complete future event data is added.

## What I Learned

The models helped me practice connecting real event records with basic machine learning. I also learned that model results can look strong on a small dataset, so they need to be explained carefully.
