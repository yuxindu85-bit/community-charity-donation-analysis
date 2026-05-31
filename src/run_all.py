from analyze_booth_layout import run_analysis as run_booth_layout_analysis
from analyze_donations import run_analysis as run_donation_analysis
from analyze_inventory import run_analysis as run_inventory_analysis
from analyze_sales import run_analysis as run_sales_analysis
from clean_data import run_cleaning
from create_charts import create_all_charts
from train_price_model import train_price_models
from train_sale_success_model import train_sale_success_models


def main():
    print("Starting charity sale data workflow...")
    run_cleaning()
    run_donation_analysis()
    run_inventory_analysis()
    run_sales_analysis()
    run_booth_layout_analysis()
    create_all_charts()
    train_price_models()
    train_sale_success_models()
    print("Full charity sale analysis workflow completed successfully.")


if __name__ == "__main__":
    main()
