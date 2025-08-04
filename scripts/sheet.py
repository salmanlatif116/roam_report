import gspread
import datetime
from google.oauth2.service_account import Credentials
import pytz

# **Set timezone to Pakistan Standard Time**
pakistan_tz = pytz.timezone('Asia/Karachi')
current_datetime = datetime.datetime.now(pakistan_tz)

# **Function to Save Data to Google Sheet**
def save_to_sheet(data):
    # **Define the scope and credentials**
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file("scripts/credentials.json", scopes=scopes)
    client = gspread.authorize(creds)

    sheet_id = "1cyxktL3LBS-e_epMhUpGiLsby8qYvO2q8nsX7fQ2-74"
    workbook = client.open_by_key(sheet_id)

    # **Get existing sheet names and determine the latest week**
    existing_sheets = workbook.worksheets()
    week_numbers = [int(sheet.title[4:]) for sheet in existing_sheets if sheet.title.startswith("week") and sheet.title[4:].isdigit()]
    
    current_week = max(week_numbers) if week_numbers else 1
    new_week = current_week + 1
    new_sheet_name = f"week{new_week}"
    
    # **Check if the new sheet already exists before creating**
    if new_sheet_name not in [sheet.title for sheet in existing_sheets]:
        workbook.add_worksheet(title=new_sheet_name, rows=1000, cols=40)
        print(f"Created new sheet: {new_sheet_name}")
        
        # **Clear and add headings**
        sheet = workbook.worksheet(new_sheet_name)
        sheet.clear()
        headings = [
            "Property", "Asking Price", "Down Payment", "Monthly Payment and Interest", "Interest Rate", "Short-Term Rental Income", "Mid-Term Rental Income", "Monthly Long-Term Rental Income", "Monthly HOA", "Monthly Insurance", "Monthly Taxes", "Total Monthly Expenses","Total Utilities(Short or Mid-Term)" ,"Mortgages", "Monthly Short Term Income", "Monthly Mid Term Income", "Monthly Long Term Income", "Days on Zillow",
            # "Property Type", "Monthly Down Payment Interest", "Co-Living Income"
        ]
        sheet.insert_row(headings, 1)
        sheet.format('A1:Z1', {'horizontalAlignment': 'CENTER', 'textFormat': {'bold': True}})
    
    # **Use the latest sheet**
    sheet = workbook.worksheet(new_sheet_name)
    
    column_mapping = {
        "address": 1, "listing_price": 2, "down_payment": 3, "principal_and_interest": 4,
        "interest_rate": 5, "short_term_rental": 6, "mid_term_rental": 7, "rent_zestimate": 8, "monthly_hoa": 9,
        "monthly_insurance": 10, "monthly_taxes": 11, "totaly_monthly_expenses": 12, "total_utilities":13, "mortgage": 14,
        "short_term_income": 15, "mid_term_income": 16, "monthly_long_term_income": 17, "days_on_zillow": 18,
        # "co_living_income": 19, "property_type": 20, "monthly_downpayment_interest": 21,
    }
    
    # **Prepare rows**
    rows = []
    for item in data:
        row = [""] * len(column_mapping)
        for key, value in item.items():
            if key in column_mapping:
                col_index = column_mapping[key] - 1
                row[col_index] = value
        rows.append(row)

    # **Insert data into sheet**
    if rows:
        sheet.append_rows(rows, value_input_option="RAW")
        sheet.format(f'A2:Z{len(rows) + 1}', {'horizontalAlignment': 'CENTER', 'textFormat': {'bold': False}})
        print(f"Inserted {len(rows)} rows.")
    else:
        print("No valid data to insert.")
