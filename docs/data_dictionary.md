# Data Dictionary

## donation_records_sample.csv

- `donation_id`: anonymized donation record ID
- `donation_date`: date when the donation was recorded
- `donor_id`: anonymized donor ID, such as `Donor_001` or `Business_001`
- `donor_type`: donor group, such as Individual, Family, Local Business, or Anonymous
- `team`: team connected to the record
- `donation_amount_cny`: direct donation amount in Chinese yuan
- `payment_status`: whether the donation was received
- `note`: short non-private note about the record

## item_inventory_sample.csv

- `item_id`: anonymized item group ID
- `received_date`: date when the item group was recorded
- `item_category`: item category, such as Books, Clothes, Toys, or Snacks
- `item_name`: simple item description without private information
- `quantity`: number of items in the group
- `estimated_unit_value_cny`: estimated value for one item before the sale
- `condition`: condition of the item group
- `team`: team responsible for the item group
- `booth_area`: booth area where the item group was planned to be sold
- `status`: sold status after the event

## sale_records_sample.csv

- `sale_id`: anonymized sale record ID
- `sale_date`: date of the charity sale
- `item_id`: item group ID connected to the inventory file
- `item_category`: category of the sold item
- `booth_area`: booth area where the sale happened
- `quantity_sold`: number of items sold in this record
- `final_unit_price_cny`: final sale price for one item
- `total_sale_cny`: total sale amount, equal to quantity sold times final unit price
- `team`: team connected to the sale record
- `payment_method`: payment method used for the sale

## booth_layout_sample.csv

- `booth_id`: anonymized booth record ID
- `booth_area`: booth area name
- `main_category`: main item type assigned to the booth
- `assigned_team`: team mainly responsible for the booth
- `table_count`: number of tables planned for the booth
- `estimated_items`: planned number of items
- `actual_items`: actual number of items placed in the booth
- `notes`: short planning notes without private information

## Processed Files

- `cleaned_donations.csv`: cleaned direct donation records
- `cleaned_inventory.csv`: cleaned inventory records with estimated total value
- `cleaned_sales.csv`: cleaned sale records after total checks
- `cleaned_booth_layout.csv`: cleaned booth planning records
- `merged_event_data.csv`: inventory data joined with item-level sale totals
