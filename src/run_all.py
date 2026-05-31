from analyze_booth_layout import run_analysis as run_booth_layout_analysis
from analyze_donations import run_analysis as run_donation_analysis
from analyze_inventory import run_analysis as run_inventory_analysis
from analyze_sales import run_analysis as run_sales_analysis
from clean_data import run_cleaning
from create_charts import create_all_charts
from train_price_model import train_price_models
from train_sale_success_model import train_sale_success_models
from utils import DATA_PROCESSED_DIR, calculate_total, format_currency, load_csv


PIPELINE_STEPS = [
    ("Clean raw data", run_cleaning),
    ("Analyze donations", run_donation_analysis),
    ("Analyze inventory", run_inventory_analysis),
    ("Analyze sales", run_sales_analysis),
    ("Analyze booth layout", run_booth_layout_analysis),
    ("Create charts", create_all_charts),
    ("Train price model", train_price_models),
    ("Train sale success model", train_sale_success_models),
]


def print_final_totals():
    donations = load_csv(DATA_PROCESSED_DIR / "cleaned_donations.csv")
    sales = load_csv(DATA_PROCESSED_DIR / "cleaned_sales.csv")
    total_direct_donations = calculate_total(donations["donation_amount_cny"])
    total_sale_revenue = calculate_total(sales["total_sale_cny"])
    total_funds_raised = total_direct_donations + total_sale_revenue

    print("Final totals:")
    print(f"- Total direct donations: {format_currency(total_direct_donations)}")
    print(f"- Total sale revenue: {format_currency(total_sale_revenue)}")
    print(f"- Total funds raised: {format_currency(total_funds_raised)}")


def main():
    print("Starting charity sale data workflow...")
    for step_name, step_function in PIPELINE_STEPS:
        print(f"\nRunning step: {step_name}")
        step_function()
        print(f"Passed step: {step_name}")

    print()
    print_final_totals()
    print("Full charity sale analysis workflow completed successfully.")


if __name__ == "__main__":
    main()
