# Campus Charity Sale Analysis

This is a small Python data analysis project based on an anonymized campus
charity sale. It combines two simple records: direct donations and charity sale
transactions. The goal is to create clear summary tables, basic charts, and a
short written report for student organizers.

All personal and organization names are anonymous. Individual donors are labeled
as `Donor_001`, `Donor_002`, and so on. Business donors are labeled as
`Business_001`, `Business_002`, and so on. The dataset does not include real
student names, school names, phone numbers, or company names.

## What This Project Shows

- Reading CSV files with Python
- - Creating calculated columns with pandas
  - - Summarizing donations, sale revenue, and team results
    - - Drawing simple matplotlib charts
      - - Writing a short report from analysis results
        - - Checking totals with basic unit tests
         
          - ## Project Structure
         
          - ```text
            campus-charity-sale-analysis/
            +-- data/
                +-- donations.csv
                +-- sale_records.csv
            +-- outputs/
                +-- figures/
            +-- reports/
            +-- src/
                +-- analyze_charity_sale.py
            +-- tests/
                +-- test_analysis.py
            +-- README.md
            +-- requirements.txt
            ```

            ## How to Run

            ```bash
            pip install -r requirements.txt
            python src/analyze_charity_sale.py
            python -m unittest discover -s tests
            ```

            ## Generated Files

            Running the analysis creates:

            - `reports/event_summary.md`
            - - `reports/donor_type_summary.csv`
              - - `reports/category_summary.csv`
                - - `reports/team_summary.csv`
                  - - `reports/daily_summary.csv`
                    - - `outputs/figures/direct_donations_by_type.png`
                      - - `outputs/figures/sale_revenue_by_category.png`
                        - - `outputs/figures/team_contribution.png`
                          - - `outputs/figures/daily_contribution_trend.png`
                           
                            - ## Notes
                           
                            - This project is intentionally modest. It is designed to show careful handling of
                            - a real activity-style dataset, not advanced modeling. The most important parts
                            - are the clean data structure, reproducible script, generated report, and tests
                            - that check the totals.
                            - 
