import requests
from bs4 import BeautifulSoup
import random
import time
import logging
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from logger.config import setup_logger

logger = setup_logger()

error_logger = logging.getLogger(__name__)
error_logger.setLevel(logging.INFO)
error_file_logger = logging.FileHandler("errorUrls.log")
error_file_logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
error_file_logger.setFormatter(formatter)

error_logger.addHandler(error_file_logger)


def get_detail_url(address):
    headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "origin": "https://www.zillow.com",
    "referer": "https://www.zillow.com/ca/",
    "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    "sec-ch-ua-mobile": "?1",
    "sec-ch-ua-platform": '"Android"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36"
}
    
    proxy_params = {
        "api_key": "950f2c9a-f6f8-4bf6-805e-a5f895200dab",
        "url": f"https://www.google.com/search?q={address}+TX+zillow",
    }
    
    logger.info(f"making request to address {address} to get detail url")
    response = requests.get(
        url="https://proxy.scrapeops.io/v1/",
        headers=headers,
        params=proxy_params,
    )
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
    
        search_results = soup.find_all("div", class_="tF2Cxc")
        for detail_link in search_results:
            link = detail_link.find("a")["href"]
            formated_address = address.replace(",","-").replace(" ","-")
            if formated_address in link and link.endswith("zpid/"):
                logger.info(f"fond detail_url for address: {address}")
                return link
        
    else:
        logger.error(f"Failed to retrieve detail_url for address: {address}")
        error_logger.error(f"the edetail url not fond for address: {address}")
        return None
    


