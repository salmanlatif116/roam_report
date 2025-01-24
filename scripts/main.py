from urllib.parse import urlencode
import requests
import re
import time
import configparser
import json
from bs4 import BeautifulSoup
import html
import datetime
import concurrent.futures
import os
import sys
import logging
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sheet import save_to_sheet

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from logger.config import setup_logger
from api import get_hoa_insrance_taxes_fields
from roam import perform_web_interaction
from detail_url import get_detail_url
logger = setup_logger()

error_logger = logging.getLogger(__name__)
error_logger.setLevel(logging.INFO)
error_file_logger = logging.FileHandler("errorUrls.log")
error_file_logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
error_file_logger.setFormatter(formatter)
error_logger.addHandler(error_file_logger)

# Cleaned headers
headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "origin": "https://www.zillow.com",
    "referer": "https://www.zillow.com/ca/",
    "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    "sec-ch-ua-mobile": "?1",
    "sec-ch-ua-platform": "Android",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36"
}

SCRAPEOPS_API_KEY = '950f2c9a-f6f8-4bf6-805e-a5f895200dab'


def process_url(url,tag, attribute_id, json_path, include_keys, exclude_keys):
    try:
        json_data = extract_json_from_url(url, tag, attribute_id)
        processed_data = process_json_data(json_data, json_path, include_keys, exclude_keys)
        
        if isinstance(processed_data, (dict, list)):
            document = {
                "data": processed_data,
              
            }
            return document
        else:
            logging.error(processed_data)

    except Exception as e:
        logging.error(f"[ERROR] error processing URL {url}: {e}")


def load_parser_definition(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    parsing_method = config['Parsing Method']['method']
    tag = config['Selectors']['tag']
    attribute_id = config['Selectors']['attribute_id']
    json_path = config['Processing Instructions']['json_path']
    
    if 'Include Keys' in config:
        include_keys = config['Include Keys'].get('keys', '').split(',')
        if include_keys == ['']:
            include_keys = None
    else:
        include_keys = None
    
    if 'Exclude Keys' in config:
        exclude_keys = config['Exclude Keys'].get('keys', '').split(',')
        if exclude_keys == ['']:
            exclude_keys = []
    else:
        exclude_keys = []

    return parsing_method, tag, attribute_id, json_path, include_keys, exclude_keys

def extract_json_from_url(url, tag, attribute_id):
    try:
        proxy_params = {
              'api_key': f'{SCRAPEOPS_API_KEY}',
              'url': f'{url}', 
        }
        response = requests.get(
          url='https://proxy.scrapeops.io/v1/',
          params=urlencode(proxy_params),
          timeout=120,
        )
        
        response.raise_for_status()  

        soup = BeautifulSoup(response.content, 'html.parser')
        script_tag = soup.find(tag, id=attribute_id)
        
        if script_tag and script_tag.string:
            try:
                script_content = html.unescape(script_tag.string.strip())
                json_data = json.loads(script_content)
                return json_data
            except json.JSONDecodeError as e:
                logging.error(f"JSONDecodeError: {e}")
                logging.error(f"Error script tag content: {script_tag.string[:100]}...")  
                raise
        else:
            raise ValueError("No matching script tag found or script tag content is empty")
    except Exception as e:
        logging.error(f"Error fetching the URL: {e}")
        raise

def process_json_data(data, json_path, include_keys, exclude_keys):
    try:
        keys = json_path.split('.')
        for key in keys:
            if key not in data:
                possible_key = next((k for k in data.keys() if k.startswith(key)), None)
                if possible_key:
                    data = data[possible_key]
                else:
                    logging.error(f"Current level keys: {data.keys()}")
                    raise KeyError(f"Key '{key}' not found in the JSON data at current level.")
            else:
                data = data[key]
            
            if isinstance(data, str):
                try:
                    data = json.loads(html.unescape(data))
                except json.JSONDecodeError:
                    logging.warning(f"Value for key '{key}' is not valid JSON, proceeding with raw string value.")
                    break  

        for key in exclude_keys:
            if key in data:
                del data[key]

        if include_keys is not None and isinstance(data, dict):
            filtered_data = {k: v for k, v in data.items() if k in include_keys}
        else:
            filtered_data = data

        if isinstance(filtered_data, dict):
            for key in exclude_keys:
                if key in filtered_data:
                    del filtered_data[key]

        return filtered_data
    except (AttributeError, KeyError) as e:
        logging.error(f"error: {e}")
        logging.error(f"Current data: {data}")
        raise

def get_required_fields(url):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parser_file_path = os.path.join(script_dir, "zillowcom_property.def")
    parser_file_path_3d = os.path.join(script_dir, "zillowcom_property_3d.def")
    parser_file_path_not = os.path.join(script_dir, "zillowcom_property_not.def")
    parser_files = [parser_file_path, parser_file_path_not, parser_file_path_3d]

    for parser_file_path in parser_files:
        try:
            parsing_method, tag, attribute_id, json_path, include_keys, exclude_keys = load_parser_definition(parser_file_path)
            dcs = process_url(url, tag, attribute_id, json_path, include_keys, exclude_keys)
            
            if dcs and "data" in dcs:
                monthly_rent_zestimate = dcs["data"].get("rentZestimate", 0)
                zpid = dcs["data"].get("zpid")
                hoa_insurnace_taxes = get_hoa_insrance_taxes_fields(zpid)
                monthly = hoa_insurnace_taxes.get("data", {}).get("property", {}).get("affordabilityEstimate", {}).get("monthly", {})
                monthly_hoa_fees = monthly.get("hoaFees", 0)
                monthly_insurance = monthly.get("homeownersInsurance", 0)
                monthly_tax = monthly.get("propertyTax", 0)

                data = {
                    "rent_zestimate": monthly_rent_zestimate,
                    "monthly_hoa": monthly_hoa_fees,
                    "monthly_insurance": monthly_insurance,
                    "monthly_tax": monthly_tax
                }
                return data
        
        except Exception as e:
            error_logger.error(f"Error encountered with file {parser_file_path} and url: {url}. Error: {str(e)}")
            logger.error(f"Error encountered with file {parser_file_path} and url: {url}. Error: {str(e)}")

def perform_calculations(fields_dict):
    for key, value in fields_dict.items():
        if key not in ("mortgage_type", "address", "interest_rate"):
            value_str = str(value).replace(",", "").strip()
            if value_str.startswith("-"):  # Handle negative values correctly
                fields_dict[key] = "-" + "".join(char for char in value_str if char.isdigit() or char == ".")
            else:
                fields_dict[key] = "".join(char for char in value_str if char.isdigit() or char == ".")

    # Convert extracted numbers to correct data types
    fields_dict["down_payment"] = float(fields_dict.get("down_payment", 0) or 0)
    fields_dict["listing_price"] = float(fields_dict.get("listing_price", 0) or 0)
    fields_dict["principal_and_interest"] = float(fields_dict.get("principal_and_interest", 0) or 0)
    fields_dict["monthly_taxes"] = float(fields_dict.get("monthly_taxes", 0) or 0)
    fields_dict["monthly_insurance"] = float(fields_dict.get("monthly_insurance", 0) or 0)
    fields_dict["monthly_hoa"] = float(fields_dict.get("monthly_hoa", 0) or 0)
    fields_dict["rent_zestimate"] = float(fields_dict.get("rent_zestimate", 0) or 0)

    # Calculate HELOC payment
    heloc_payment = fields_dict["down_payment"] * 0.00573

    # Calculate monthly net income
    monthly_net_income = (
        fields_dict["rent_zestimate"]
        - fields_dict["principal_and_interest"]
        - fields_dict["monthly_taxes"]
        - fields_dict["monthly_insurance"]
        - fields_dict["monthly_hoa"]
        - heloc_payment
    )

    # Calculate mortgage
    mortgage = fields_dict["listing_price"] - fields_dict["down_payment"]

    # Calculate monthly down payment and interest
    monthly_downpayment_and_interest = fields_dict["down_payment"] * 0.00573

    # Update dictionary with calculated values
    fields_dict["mortgage"] = mortgage
    fields_dict["monthly_downpayment_and_interest"] = monthly_downpayment_and_interest
    fields_dict["monthly_net_income"] = monthly_net_income

    # Formatting values for display
    for key, value in fields_dict.items():
        if key not in {"address", "interest_rate", "mortgage_type"}:
            if isinstance(value, (int, float)):
                fields_dict[key] = "-${:,.2f}".format(abs(value)) if value < 0 else "${:,.2f}".format(value)

    # Ensure rent_zestimate is properly formatted
    if not fields_dict["rent_zestimate"]:
        fields_dict["rent_zestimate"] = "$0.00"

    return fields_dict




if __name__ == "__main__":
    # while True:
    #     roam_data =  perform_web_interaction()
    #     if roam_data:
    #         break
    
         
    with open("roam_data.json","r") as file:
        roam_fields = json.load(file)
    for fields in roam_fields:
        full_address = fields.get("address","")
        address = full_address[:full_address.find(",")]
        time.sleep(5)
        detail_url = get_detail_url(address)
        
        if detail_url:
            with open("urls.json","a") as file:
                file.write(str(detail_url) + "\n")
            logger.info(f"Fetching rent_zestimate, HOA, insurance, and taxes of url: {detail_url}.")
            zillow_fields = get_required_fields(detail_url)
            if not zillow_fields:
                error_logger.error(f"fields not fond against detail_url: {detail_url}")
    
            if fields:
                if zillow_fields is None:
                    fields["monthly_insurance"] = 0
                    fields["rent_zestimate"] = 0
                    fields["monthly_hoa"] = 0
                    fields["monthly_taxes"] = 0
                    fields["mortgage_type"] = "VA"

                else:
                    fields["mortgage_type"] = "VA"
                    fields["rent_zestimate"] = zillow_fields.get("rent_zestimate",0) if zillow_fields.get("rent_zestimate") else "N/A"
                    fields["monthly_hoa"] = zillow_fields.get("monthly_hoa",0)
                    fields["monthly_insurance"] = zillow_fields.get("monthly_insurance",0)
                    fields["monthly_taxes"] = zillow_fields.get("monthly_tax",0)
                    
                with open("calculated_results.json", "a") as file:
                    calculated_fields = perform_calculations(fields)
                    json_data = json.dumps(calculated_fields)
                    print(json_data)
                    file.write(json_data + "\n") 
                with open("calculated_results.json", "r") as file:
                    data = [json.loads(line.strip()) for line in file if line.strip()]
                    save_to_sheet(data)

            else:
                logger.error("An error occurred fetching rent_zestimate, HOA, insurance, and taxes fields.")
        else:
            logger.info("No detail URL found for the given address.")


