# Data Dictionary

I added this file so the cleaned CSV files are easier to understand. The
original event records were not in a perfect data format, so I had to decide how
to name columns, group values, and keep private information out of the project.

This document explains the two source files in the `data/` folder.

## File: data/donations.csv

This file stores direct donation records.

record_id: A simple row ID for each donation record. Example: `D001`.

received_date: The date when the donation was recorded as received. I use the
`YYYY-MM-DD` format so pandas can read it as a date.

team: The volunteer team that handled or entered the record. I use simple labels
such as `Team A`, `Team B`, and `Team C`.

donor_id: An anonymous donor label. Real names and business names were removed.
Examples include `Donor_001` and `Business_001`.

donor_type: A general donor group, such as `Individual`, `Local Business`, or
`Community Group`.

amount_cny: The donation amount in Chinese yuan.

payment_status: A cleaned status field. In this version of the project, the
records included in the analysis are marked as `Received`.

## File: data/sale_records.csv

This file stores item-level charity sale records.

sale_id: A simple row ID for each sale record. Example: `S001`.

event_day: The date when the sale happened. I use the `YYYY-MM-DD` format.

team: The volunteer team that handled the sale record.

item_category: A simplified item category. I grouped similar items together so
the chart would be easier to read.

quantity: The number of items sold in that category and record.

unit_price_cny: The selling price per item in Chinese yuan.

cost_cny: The simple cost estimate for the items in that record. This is used
to calculate net contribution from the sale.

## Calculated Columns

The script creates these columns while running the analysis. They are not stored
directly in the raw CSV files.

revenue_cny: `quantity * unit_price_cny`

net_contribution_cny: `revenue_cny - cost_cny`

total_contribution_cny: Direct donations plus sale net contribution, depending
on the summary table.

## Anonymization Notes

I removed real names, phone numbers, school names, and organization names before
making the GitHub version of the project.

I also changed business names into simple English labels because I wanted the
project to focus on data analysis instead of personal or local information.

The team names are also simplified. They do not represent official team names.

## Limits Of The Data

This dataset is useful for learning and basic review, but it is not an official
financial record.

Some original information came from handwritten or informal activity records, so
I cleaned the data before using it in Python.

The sale cost field is simple. For a future version, I would record cost details
more carefully during the event instead of cleaning them afterward.
