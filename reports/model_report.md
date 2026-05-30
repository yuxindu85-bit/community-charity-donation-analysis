# Simple Machine Learning Model Report

## Purpose

This report summarizes two beginner-friendly machine learning experiments for the charity sale project. The models are exploratory learning tools, not official financial or operational prediction systems.

## Price Prediction Regression Model

Goal: predict final item sale price using item category, condition, estimated value, booth area, team, and quantity.

| Model | MAE | RMSE | R2 score |
| --- | ---: | ---: | ---: |
| Linear Regression | 1.622 | 2.128 | 0.987 |
| Random Forest Regressor | 2.747 | 4.53 | 0.943 |

## Sale Success Classification Model

Goal: predict whether an item group is likely to sell based on category, condition, estimated value, booth area, team, and quantity.

| Model | Accuracy | Precision | Recall |
| --- | ---: | ---: | ---: |

Class balance: 27 sold or partially sold item groups and 4 unsold item groups.
| Logistic Regression | 1.0 | 1.0 | 1.0 |
| Decision Tree Classifier | 0.8 | 1.0 | 0.778 |

## Limitations

- The dataset is small and anonymized.
- The sale success dataset is imbalanced, so high accuracy should not be over-interpreted.
- The models are useful for learning and reflection, not official decision-making.
- Some sale outcomes may depend on booth traffic, buyer interest, weather, and timing, which were not fully recorded.
- Model results can change if more complete future event data is added.
