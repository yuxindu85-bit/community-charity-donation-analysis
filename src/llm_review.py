import argparse
import json
import os
from pathlib import Path

import pandas as pd

from utils import PROJECT_ROOT, SUMMARY_DIR, ensure_directory, format_currency


DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "reports" / "llm_operation_review.md"
OPENAI_DEFAULT_MODEL = "gpt-5-mini"
DEEPSEEK_DEFAULT_MODEL = "deepseek-v4-flash"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"


def load_optional_csv(path):
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def load_event_context():
    donation_summary = load_optional_csv(SUMMARY_DIR / "donation_summary.csv")
    donation_by_team = load_optional_csv(SUMMARY_DIR / "donation_by_team.csv")
    sales_by_category = load_optional_csv(SUMMARY_DIR / "sales_by_category.csv")
    sales_by_team = load_optional_csv(SUMMARY_DIR / "sales_by_team.csv")
    booth_summary = load_optional_csv(SUMMARY_DIR / "booth_summary.csv")
    estimate_vs_actual = load_optional_csv(
        SUMMARY_DIR / "estimate_vs_actual_summary.csv"
    )
    metrics_path = PROJECT_ROOT / "models" / "model_metrics.json"
    model_metrics = {}
    if metrics_path.exists():
        model_metrics = json.loads(metrics_path.read_text(encoding="utf-8"))

    total_direct_donations = (
        donation_summary["total_donation_cny"].sum()
        if not donation_summary.empty
        else 0
    )
    total_sale_revenue = (
        sales_by_category["sale_revenue_cny"].sum()
        if not sales_by_category.empty
        else 0
    )
    total_funds = total_direct_donations + total_sale_revenue

    return {
        "total_direct_donations": total_direct_donations,
        "total_sale_revenue": total_sale_revenue,
        "total_funds": total_funds,
        "top_donor_type": top_value(donation_summary, "donor_type"),
        "top_donation_team": top_value(donation_by_team, "team"),
        "top_sale_category": top_value(sales_by_category, "item_category"),
        "top_sale_team": top_value(sales_by_team, "team"),
        "top_booth": top_value(booth_summary, "booth_area"),
        "estimate_notes": summarize_estimate_gap(estimate_vs_actual),
        "model_metrics": model_metrics,
    }


def top_value(dataframe, column):
    if dataframe.empty or column not in dataframe.columns:
        return "Not available"
    return str(dataframe.iloc[0][column])


def summarize_estimate_gap(dataframe):
    if dataframe.empty or "price_difference_cny" not in dataframe.columns:
        return "Estimate-vs-actual data is not available."

    largest_gap = dataframe.copy()
    largest_gap["absolute_gap"] = largest_gap["price_difference_cny"].abs()
    row = largest_gap.sort_values("absolute_gap", ascending=False).iloc[0]
    return (
        f"{row['item_category']} had the largest estimate gap "
        f"({format_currency(row['price_difference_cny'])})."
    )


def build_review_prompt(context):
    return f"""You are helping review an anonymized community charity sale data project.

Write a concise student-style operations reflection. Keep the tone honest,
practical, and not overclaimed. This is not an official financial report.
Do not describe it as a professional audit, automated decision system, or
fundraising platform.

Use these project facts:
- Total direct donations: {format_currency(context['total_direct_donations'])}
- Total sale revenue: {format_currency(context['total_sale_revenue'])}
- Total funds raised in the sample analysis: {format_currency(context['total_funds'])}
- Top donor type: {context['top_donor_type']}
- Top donation team: {context['top_donation_team']}
- Top sale category: {context['top_sale_category']}
- Top sale team: {context['top_sale_team']}
- Top booth area: {context['top_booth']}
- Estimate review note: {context['estimate_notes']}

Also mention that the dataset is anonymized and sample-based. Explain that the
machine learning results are exploratory and may look strong because the sample
dataset is small and simple.

Return Markdown with these sections:
1. Data-supported observations
2. Operational lessons
3. Limitations
4. Possible next improvements
"""


def generate_offline_review(context):
    return f"""# Optional LLM Operation Review Draft

This draft was generated in offline mode. It does not use GPT or DeepSeek, but
it follows the same event context that would be sent to an LLM if API keys were
configured.

## Data-supported observations

- Total direct donations were {format_currency(context['total_direct_donations'])}.
- Sale revenue was {format_currency(context['total_sale_revenue'])}.
- The combined sample total was {format_currency(context['total_funds'])}.
- The top sale category was {context['top_sale_category']}.
- The strongest booth area by revenue was {context['top_booth']}.
- {context['estimate_notes']}

## Operational lessons

The data suggests that simple tracking can help a charity sale team review item
allocation, booth planning, and team contribution after the event. The records
also make it easier to compare estimated item values with actual sale prices.

## Limitations

The dataset is anonymized and sample-based. It should not be treated as an
official financial report. The machine learning results are exploratory, and
high scores may reflect simple patterns in a small dataset.

## Possible next improvements

- Improve item labels before the event.
- Track sale time and booth traffic.
- Collect buyer feedback if privacy rules allow it.
- Reuse the dashboard and data template for future charity sale reviews.
"""


def call_openai(prompt, model=None):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is required for provider=openai.")

    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=model or os.environ.get("OPENAI_MODEL", OPENAI_DEFAULT_MODEL),
        input=prompt,
    )
    return response.output_text


def call_deepseek(prompt, model=None):
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY is required for provider=deepseek.")

    from openai import OpenAI

    client = OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)
    response = client.chat.completions.create(
        model=model or os.environ.get("DEEPSEEK_MODEL", DEEPSEEK_DEFAULT_MODEL),
        messages=[
            {
                "role": "system",
                "content": "You write concise, honest student project reflections.",
            },
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content


def generate_llm_review(provider, output_path=DEFAULT_OUTPUT_PATH, model=None):
    context = load_event_context()
    prompt = build_review_prompt(context)

    if provider == "offline":
        review_text = generate_offline_review(context)
    elif provider == "openai":
        review_text = call_openai(prompt, model=model)
    elif provider == "deepseek":
        review_text = call_deepseek(prompt, model=model)
    else:
        raise ValueError(f"Unsupported provider: {provider}")

    output_path = Path(output_path)
    ensure_directory(output_path.parent)
    output_path.write_text(review_text.strip() + "\n", encoding="utf-8")
    return output_path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate an optional GPT or DeepSeek operation review draft."
    )
    parser.add_argument(
        "--provider",
        choices=["offline", "openai", "deepseek"],
        default=os.environ.get("LLM_PROVIDER", "offline"),
        help="LLM provider to use. Defaults to offline mode.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Optional model override, such as gpt-5-mini or deepseek-v4-flash.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_PATH),
        help="Markdown output path.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    output_path = generate_llm_review(
        provider=args.provider,
        output_path=args.output,
        model=args.model,
    )
    print(f"LLM review draft saved to {output_path}")


if __name__ == "__main__":
    main()
