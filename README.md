# Community Charity Sale Data Operations Analysis

## Project Overview

This project analyzes anonymized donation, inventory, sale, and booth planning
records from a charity sale that raised over ¥26,000. I supported the data and
operations side of the event by organizing item records, estimating values,
maintaining online spreadsheets, helping with item allocation and booth
planning, tracking preparation progress, and reviewing post-event data.

The project uses Python, pandas, matplotlib, scikit-learn, and Streamlit to turn
event records into cleaned data, summary tables, charts, reports, simple model
experiments, and an interactive dashboard.

## My Role

- Counted and categorized donated items before the event
- Estimated item values before the sale
- Maintained online spreadsheets for donations, items, and preparation progress
- Supported item allocation across teams and booth areas
- Helped organize booth layout planning
- Reviewed post-event donation, inventory, sale, and booth records
- Built this anonymized Python analysis project after the event

## Why This Project Matters

Charity sale work is not only about collecting and selling items. When many
items, donors, teams, and booth areas are involved, simple data organization can
make the event easier to prepare and review. This project shows how clear
records helped connect community service with basic data analysis and operations
planning.

## Tools Used

- Python
- pandas
- matplotlib
- scikit-learn
- Streamlit
- Plotly
- Jupyter Notebook
- CSV files
- unittest

## Dataset Description

The sample data is anonymized and based on the structure of the event records.
It does not include real names, phone numbers, school names, organization names,
addresses, or private donor information.

- `donation_records_sample.csv`: direct donation records by donor type and team
- `item_inventory_sample.csv`: donated item categories, quantities, estimated values, and booth areas
- `sale_records_sample.csv`: item-level sale records and payment methods
- `booth_layout_sample.csv`: booth planning records and item allocation notes

## Project Workflow

1. Collect donation, inventory, sale, and booth planning records
2. Remove or replace private information
3. Clean CSV files and standardize categories and team names
4. Check sale totals against quantity and unit price
5. Create processed data files
6. Analyze donations, inventory, sales, and booth layout
7. Generate summary tables
8. Create charts
9. Run simple machine learning experiments for event review
10. Write final event reports and reflection notes
11. Run unit tests to check the main calculations and outputs

## Key Results

- Total direct donations: ¥22,190
- Total charity sale revenue: ¥5,269
- Total funds raised in the sample analysis: ¥27,459
- Direct donations made up the larger part of the total funds
- Shared Table and Booth A were important areas because they handled many small items
- Handmade crafts, books, and stationery were useful categories for reviewing estimate vs actual prices
- Team contribution summaries helped compare donation and sale support together

## Key Visualizations

![Revenue by category](reports/charts/revenue_by_category.png)

![Item quantity by category](reports/charts/item_quantity_by_category.png)

![Team contribution](reports/charts/team_contribution.png)

![Estimate vs actual price](reports/charts/estimate_vs_actual_price.png)

![Booth revenue comparison](reports/charts/booth_revenue_comparison.png)

![Donation source breakdown](reports/charts/donation_source_breakdown.png)

## Simple Machine Learning Experiments

I added two beginner-friendly machine learning experiments to explore the
charity sale data.

The first model predicts final item sale price using item category, condition,
estimated value, booth area, team, and quantity. It compares Linear Regression
and Random Forest Regressor models using MAE, RMSE, and R2 score.

The second model predicts whether an item group is likely to sell. It compares
Logistic Regression and Decision Tree Classifier models using accuracy,
precision, recall, and a confusion matrix.

These models are not used for official decision-making because the dataset is
small and anonymized. They are included to help me understand how basic machine
learning can be used to review real community event data.

Current sample results:

- Linear Regression price model: MAE 1.622, RMSE 2.128, R2 0.987
- Random Forest price model: MAE 2.747, RMSE 4.530, R2 0.943
- Logistic Regression sale success model: accuracy 1.000, precision 1.000, recall 1.000
- Decision Tree sale success model: accuracy 0.800, precision 1.000, recall 0.778

The classification result should be read carefully because the sample dataset
has many more sold item groups than unsold item groups.

![Predicted vs actual price](reports/charts/predicted_vs_actual_price.png)

![Price model feature importance](reports/charts/feature_importance_price.png)

![Sale success confusion matrix](reports/charts/sale_success_confusion_matrix.png)

![Model comparison](reports/charts/model_comparison.png)

The full model notes are in `reports/model_report.md`.

## Interactive Dashboard

I also created a Streamlit dashboard to make the results easier to explore. The
dashboard allows users to filter the data by team, item category, booth area,
and item condition. It shows donation summaries, sale revenue, booth
performance, team contribution, estimate-versus-actual price comparisons, and
model metrics if they have been generated.

## How to Run

Install the requirements:

```bash
pip install -r requirements.txt
```

Run the full project workflow:

```bash
python src/clean_data.py
python src/analyze_donations.py
python src/analyze_inventory.py
python src/analyze_sales.py
python src/analyze_booth_layout.py
python src/create_charts.py
python src/train_price_model.py
python src/train_sale_success_model.py
python -m unittest discover -s tests
```

Run the dashboard:

```bash
streamlit run dashboard/app.py
```

## Project Structure

```text
community-charity-donation-analysis/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── raw/
│   └── processed/
├── src/
├── dashboard/
├── models/
├── reports/
│   ├── summary_tables/
│   └── charts/
├── docs/
├── notebooks/
└── tests/
```

## Data Privacy Note

All data in this repository is anonymized and sample-based. Donor names, phone
numbers, school names, organization names, addresses, and other private details
are not included. The project is for learning and event review, not official
financial accounting.

## What I Learned

Before this project, I thought charity sale work was mostly about collecting
and selling items. After working on the data side, I learned that clear records
also matter. Good spreadsheets helped with item allocation, booth planning,
progress tracking, and post-event review. I also practiced turning messy event
records into a simple analysis workflow that can be run again.

## Future Improvements

- Add item ID labels or barcodes for easier tracking
- Track sale time to understand busy periods
- Track booth visitor flow
- Improve the estimate vs actual price comparison
- Add sale time and visitor-flow data to the dashboard if future records include it
- Create a reusable data collection template for future charity sales
