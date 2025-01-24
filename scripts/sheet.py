import gspread
import json
from google.oauth2.service_account import Credentials

# Define the scope and credentials
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("scripts/credentials.json", scopes=scopes)
client = gspread.authorize(creds)


workbook = client.open_by_key(sheet_id)
sheet = workbook.worksheet('roam_report')

sheet.clear()

# Add heading
headings = [
    "Address",
    "Asking Price",
    "Down Payment",
    "Monthly Payment and Interest",
    "Interest Rate",
    "Mortgage Type",
    "Monthly Long-Term Rental Income",
    "Monthly HOA",
    "Monthly Insurance",
    "Monthly Taxes",
    "Mortgages",
    "Monthly Down Payment Interest",
    "Monthly Net Income",
]
sheet.insert_row(headings, 1)

header_format = {
    'horizontalAlignment': 'CENTER',
    'textFormat': {'bold': True},
}
sheet.format('A1:O1', header_format)

# Define the mapping of keys to column indices
column_mapping = {
    "address": 1,
    "listing_price": 2,
    "down_payment": 3,
    "principal_and_interest": 4,
    "interest_rate": 5,
    "mortgage_type": 6,
    "rent_zestimate": 7,
    "monthly_hoa": 8,
    "monthly_insurance": 9,
    "monthly_taxes": 10,
    "mortgage": 11,
    "monthly_downpayment_and_interest": 12,
    "monthly_net_income": 13,
}

# Read and parse data
with open("calculated_results.json", "r") as file:
    data = file.readlines()

parsed_data = []
for line in data:
    try:
        parsed_data.append(json.loads(line.strip()))
    except json.JSONDecodeError as e:
        print(f"Skipping invalid JSON line: {line.strip()}")

# Insert rows
rows = []
for item in parsed_data:
    row = [""] * len(headings)
    for key, value in item.items():
        if key in column_mapping:
            col_index = column_mapping[key] - 1
            row[col_index] = value
    rows.append(row)

if rows:
    sheet.append_rows(rows, value_input_option="RAW")
    content_format = {'horizontalAlignment': 'CENTER'}
    sheet.format(f'A2:O{len(rows) + 1}', content_format)
    print(f"Inserted {len(rows)} rows.")
else:
    print("No valid data to insert.")
