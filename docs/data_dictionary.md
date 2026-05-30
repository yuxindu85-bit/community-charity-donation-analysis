# Data Dictionary

This document explains the sample datasets used in the project. The data is
anonymized and cleaned for learning purposes.

## `data/raw/donation_records_sample.csv`

Direct donation records.

- `record_id`: Unique ID for each donation record.
- `donation_date`: Date when the donation was recorded.
- `team`: Volunteer team connected with the record.
- `donor_id`: Anonymous donor label, such as `Donor_001` or `Business_001`.
- `donor_type`: Type of donor, such as individual, local business, or community
  group.
- `donation_amount`: Direct donation amount in CNY.

## `data/raw/sale_records_sample.csv`

Records for items sold during the charity sale.

- `sale_id`: Unique ID for each sale record.
- `sale_date`: Date when the item was sold.
- `team`: Team that handled the sale record.
- `item_id`: Item ID that connects the sale record with the inventory table.
- `item_category`: Item group, such as books, clothes, toys, or stationery.
- `item_name`: Simple item description.
- `quantity`: Number of items sold.
- `final_sale_price`: Final price per item in CNY.

## `data/raw/item_inventory_sample.csv`

Preparation records for donated items.

- `item_id`: Unique item ID.
- `item_category`: Item group.
- `item_name`: Simple item description.
- `estimated_value`: Estimated value per item in CNY before the sale.
- `quantity`: Number of donated items recorded before the sale.
- `booth_area`: Planned booth or display area.
- `team`: Team responsible for the item group.
- `preparation_status`: Preparation status before the sale.

## `data/processed/cleaned_charity_sale_data.csv`

Cleaned dataset created by `src/clean_data.py`.

- `record_id`: Original donation ID or sale ID.
- `record_type`: `direct_donation` or `charity_sale`.
- `date`: Donation date or sale date.
- `team`: Standardized team name.
- `donor_id`: Anonymous donor ID for direct donations.
- `donor_type`: Donor type for direct donations.
- `item_id`: Item ID for sale records.
- `item_category`: Sale category or `Direct Donation`.
- `item_name`: Item description for sale records.
- `quantity`: Number of items sold, or 1 for direct donations.
- `estimated_value`: Estimated item value or donation amount.
- `final_sale_price`: Final sale price per item. Direct donations use 0.
- `amount_cny`: Donation amount or sale revenue in CNY.
- `booth_area`: Booth area for sale records.
