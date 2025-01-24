import gspread
import json
from google.oauth2.service_account import Credentials

def save_to_sheet(data, sheet_name='roam_report'):
    """
    Saves the provided data to the specified Google Sheet.
    
    :param data: List of dictionaries containing the data to save.
    :param sheet_name: Name of the worksheet to update (default: 'roam_report').
    """
    # Define the scope and credentials
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file("scripts/credentials.json", scopes=scopes)
    client = gspread.authorize(creds)
    
    sheet_id = "1cyxktL3LBS-e_epMhUpGiLsby8qYvO2q8nsX7fQ2-74"
    workbook = client.open_by_key(sheet_id)
    sheet = workbook.worksheet(sheet_name)
    
    sheet.clear()
    
    # Define headings
    headings = [
        "Address", "Asking Price", "Down Payment", "Monthly Payment and Interest", "Interest Rate", 
        "Mortgage Type", "Monthly Long-Term Rental Income", "Monthly HOA", "Monthly Insurance", 
        "Monthly Taxes", "Mortgages", "Monthly Down Payment Interest", "Monthly Net Income"
    ]
    sheet.insert_row(headings, 1)
    
    header_format = {
        'horizontalAlignment': 'CENTER',
        'textFormat': {'bold': True},
    }
    sheet.format('A1:M1', header_format)
    
    # Define the mapping of keys to column indices
    column_mapping = {
        "address": 1, "listing_price": 2, "down_payment": 3, "principal_and_interest": 4,
        "interest_rate": 5, "mortgage_type": 6, "rent_zestimate": 7, "monthly_hoa": 8,
        "monthly_insurance": 9, "monthly_taxes": 10, "mortgage": 11,
        "monthly_downpayment_and_interest": 12, "monthly_net_income": 13
    }
    
    # Prepare rows
    rows = []
    for item in data:
        row = [""] * len(headings)
        for key, value in item.items():
            if key in column_mapping:
                col_index = column_mapping[key] - 1
                row[col_index] = value
        rows.append(row)
    
    if rows:
        sheet.append_rows(rows, value_input_option="RAW")
        content_format = {'horizontalAlignment': 'CENTER'}
        sheet.format(f'A2:M{len(rows) + 1}', content_format)
        print(f"Inserted {len(rows)} rows.")
    else:
        print("No valid data to insert.")
