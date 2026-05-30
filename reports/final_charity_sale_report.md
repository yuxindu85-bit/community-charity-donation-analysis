# Final Charity Sale Report

## Overview

This report summarizes an anonymized charity sale dataset. The event combined
direct donations with income from donated items. In this sample dataset, direct
donations totaled 23,090 CNY and charity sale revenue totaled
4,821 CNY. The combined total was 27,911 CNY.

## Data Sources

The project uses three sample CSV files:

- `donation_records_sample.csv` for direct donation records
- `sale_records_sample.csv` for sold item records
- `item_inventory_sample.csv` for item categories, estimated values, and booth
  planning information

All private names, phone numbers, school names, and organization names were
removed or replaced with anonymous labels before analysis.

## Main Findings

- The individual donor group was the largest direct donation source.
- Handmade Crafts produced the highest sale revenue among item categories.
- Team A had the highest combined contribution from donations and sales.
- Direct donations were larger than sale revenue, which makes sense because a
  few donors gave larger one-time amounts while most sale items were lower-priced
  donated goods.

## How The Data Supported Event Planning

Keeping item and donation records in spreadsheets made the event easier to
organize. The item categories helped with booth layout, the estimated values
helped with price planning, and the team summaries helped review preparation
work after the event.

## Limitations

This is not an official financial audit. The dataset is a cleaned and anonymized
learning version of the event records. Some item descriptions were simplified,
and the data does not include exact sale time for each item.

## Future Improvements

- Track item IDs more carefully from donation to sale.
- Compare estimated item value with final sale price.
- Add booth-level or time-level sale information.
- Add more tests for category and team totals.

## Reflection

This project helped me understand that community service also depends on clear
organization. Counting items, cleaning records, and checking totals made the
post-event review more useful than a simple list of numbers.
