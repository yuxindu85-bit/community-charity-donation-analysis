# Charity Sale Analysis Walkthrough

This Markdown walkthrough presents the analysis in a GitHub-friendly format.
It is designed for quick review without needing to open or run a separate notebook file.

Before using this walkthrough, run the full project pipeline from the repository root:

```bash
python src/run_all.py
```

## 1. Introduction

This project uses anonymized donation, inventory, sale, and booth planning records from a community charity sale.
The data is sample-based and does not include private names, contact information, school names, organization names, addresses, QR codes, or payment details.

The goal of the walkthrough is to show how the cleaned data can be loaded, summarized, and reviewed without reading every Python script.

## 2. Load Cleaned Data

The walkthrough starts by locating the project root and the generated output folders.

```python
from pathlib import Path
import json
import pandas as pd

PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
SUMMARY_DIR = PROJECT_ROOT / "reports" / "summary_tables"
METRICS_PATH = PROJECT_ROOT / "models" / "model_metrics.json"
```

It then checks that the required processed files exist.
If they are missing, the user should run `python src/run_all.py` first.

```python
required_files = [
    PROCESSED_DIR / "cleaned_donations.csv",
    PROCESSED_DIR / "cleaned_inventory.csv",
    PROCESSED_DIR / "cleaned_sales.csv",
    PROCESSED_DIR / "merged_event_data.csv",
    SUMMARY_DIR / "booth_summary.csv",
    SUMMARY_DIR / "estimate_vs_actual_summary.csv",
]
```

## 3. Donation Analysis

The donation analysis reviews direct donations by donor type and total donation amount.

```python
donations = pd.read_csv(PROCESSED_DIR / "cleaned_donations.csv")
donation_summary = donations.groupby("donor_type", as_index=False)["donation_amount_cny"].sum()
total_direct_donations = donations["donation_amount_cny"].sum()
```

In the current sample data, direct donations make up the largest part of the total funds raised.

## 4. Inventory Analysis

The inventory analysis groups donated item records by category.
This helps show which categories had the most donated items and the largest estimated value.

```python
inventory = pd.read_csv(PROCESSED_DIR / "cleaned_inventory.csv")
inventory_summary = inventory.groupby("item_category", as_index=False).agg(
    total_quantity=("quantity", "sum"),
    estimated_total_value_cny=("estimated_total_value_cny", "sum"),
)
```

This step connects the operations side of the event with the data side.
Clear categories made it easier to plan booths, estimate display space, and review what happened after the event.

## 5. Sales Analysis

The sales analysis groups sale revenue by item category.

```python
sales = pd.read_csv(PROCESSED_DIR / "cleaned_sales.csv")
sales_summary = sales.groupby("item_category", as_index=False).agg(
    quantity_sold=("quantity_sold", "sum"),
    sale_revenue_cny=("total_sale_cny", "sum"),
)
total_sale_revenue = sales["total_sale_cny"].sum()
total_funds = total_direct_donations + total_sale_revenue
```

The combined total funds raised in the sample project are over ¥26,000.
This is not an official financial report; it is an anonymized analysis project based on event records.

## 6. Booth Layout Analysis

The booth layout summary connects booth planning information with sale revenue.

```python
booth_summary = pd.read_csv(SUMMARY_DIR / "booth_summary.csv")
booth_summary[
    ["booth_area", "assigned_team", "main_category", "actual_items", "booth_revenue_cny"]
]
```

This helps review whether item allocation and booth placement were reasonable.

## 7. Estimate vs Actual Price

The estimate vs actual price table compares estimated sold value with final sale revenue by category.

```python
estimate_vs_actual = pd.read_csv(SUMMARY_DIR / "estimate_vs_actual_summary.csv")
estimate_vs_actual[
    ["item_category", "estimated_sold_value_cny", "actual_sale_total_cny", "price_difference_cny"]
]
```

This comparison is useful for reflecting on pricing decisions.
Estimated values are helpful for planning, but final prices also depend on buyer interest and event conditions.

## 8. Simple Machine Learning Results

The project includes beginner-friendly exploratory machine learning experiments.
The walkthrough loads the saved model metrics if they exist.

```python
if METRICS_PATH.exists():
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
else:
    metrics = {}
```

These models are exploratory learning models.
They should not be used for official price decisions or event planning decisions because the dataset is small and anonymized.

## 9. Key Findings

- Direct donations made up the largest part of the total funds.
- Sale records were useful for reviewing category and booth performance.
- Item IDs made it possible to connect inventory and sale records.
- Estimate vs actual price comparison helped review pricing choices.
- The simple ML results are useful for learning, but not official decision-making.

## 10. Reflection

Before this project, I thought charity sale work was mostly about collecting and selling items.
After working on the data side, I learned that clear records, item categories, estimated values, and simple analysis can make an event easier to organize and improve.

This project helped connect community service, operations, and data analysis in a practical way.
