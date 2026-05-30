# Community Charity Sale Data Operations Analysis

## Project Overview

This project analyzes anonymized donation, inventory, sale, and booth planning
records from a charity sale that raised over ¥26,000. I supported the data and
operations side of the event by organizing item records, estimating values,
maintaining online spreadsheets, helping with item allocation and booth
planning, tracking preparation progress, and reviewing post-event data.

The project uses Python, pandas, and matplotlib to turn event records into
cleaned data, summary tables, charts, and short review reports.

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
9. Write final event reports and reflection notes
10. Run unit tests to check the main calculations and outputs

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
python -m unittest discover -s tests
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
- Build a simple dashboard in the future
- Create a reusable data collection template for future charity sales
