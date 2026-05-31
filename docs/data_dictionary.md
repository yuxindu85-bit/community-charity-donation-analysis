# Data Dictionary

## donation_records_sample.csv

| Column | Meaning | Example |
| --- | --- | --- |
| donation_id | Anonymized donation record ID | D001 |
| donation_date | Date when the donation was recorded | 2026-05-10 |
| donor_id | Anonymized donor ID | Donor_001 |
| donor_type | Donor group | Individual |
| team | Team connected to the record | Team A |
| donation_amount_cny | Direct donation amount in Chinese yuan | 388 |
| payment_status | Payment status in the sample record | Received |
| note | Short non-private note | individual donation |

## item_inventory_sample.csv

| Column | Meaning | Example |
| --- | --- | --- |
| item_id | Anonymized item group ID | I001 |
| received_date | Date when the item group was recorded | 2026-05-13 |
| item_category | Item category | Books |
| item_name | Simple item description without private information | Story Books |
| quantity | Number of items in the group | 18 |
| estimated_unit_value_cny | Estimated value for one item before the sale | 18 |
| condition | Condition of the item group | Good |
| team | Team responsible for the item group | Team A |
| booth_area | Planned booth area | Booth A |
| status | Post-event sale status | Sold |

## sale_records_sample.csv

| Column | Meaning | Example |
| --- | --- | --- |
| sale_id | Anonymized sale record ID | S001 |
| sale_date | Date of the charity sale | 2026-05-23 |
| item_id | Item group ID connected to inventory | I001 |
| item_category | Category of the sold item | Books |
| booth_area | Booth area where the sale happened | Booth A |
| quantity_sold | Number of items sold in this record | 8 |
| final_unit_price_cny | Final sale price for one item | 16 |
| total_sale_cny | Quantity sold times final unit price | 128 |
| team | Team connected to the sale record | Team A |
| payment_method | Sample payment method | WeChat Pay |

## booth_layout_sample.csv

| Column | Meaning | Example |
| --- | --- | --- |
| booth_id | Anonymized booth section record ID | B001A |
| booth_area | Booth area name | Booth A |
| main_category | Main item type assigned to the booth section | Books |
| assigned_team | Team mainly responsible for the booth | Team A |
| table_count | Number of tables planned for the booth section | 2 |
| estimated_items | Planned number of items | 95 |
| actual_items | Actual number of items placed in the booth section | 95 |
| notes | Short planning note without private information | placed lower-priced books near notebooks |

## Processed Files

| File | Meaning |
| --- | --- |
| cleaned_donations.csv | Cleaned direct donation records |
| cleaned_inventory.csv | Cleaned inventory records with estimated total value |
| cleaned_sales.csv | Cleaned sale records after total checks |
| cleaned_booth_layout.csv | Cleaned booth planning records |
| merged_event_data.csv | Inventory data joined with item-level sale totals |
