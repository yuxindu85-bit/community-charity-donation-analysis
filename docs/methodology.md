# Methodology

The analysis uses a simple workflow that can be checked and repeated.

## Data Cleaning

The cleaning script loads the raw CSV files, removes extra spaces in text
columns, standardizes category names and team names, checks sale totals, and
saves cleaned files in `data/processed/`.

## Donation Analysis

Direct donations are grouped by donor type and team. The script calculates the
total amount, number of records, average donation amount, and share of total
direct donations.

## Inventory Analysis

Inventory records are grouped by item category, team, and status. Estimated
total value is calculated by multiplying quantity by estimated unit value.

## Sales Analysis

Sale records are grouped by item category, booth area, and team. The script
also compares estimated sold value with actual sale revenue by joining sale
records with inventory records through `item_id`.

## Booth Layout Review

Booth layout records are joined with sale records by booth area. This helps
compare planned item counts, actual item counts, and booth-level revenue.

## Limitations

The analysis is based on anonymized sample records. It is useful for event
review, but it should not be treated as official accounting.
