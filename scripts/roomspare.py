from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import os
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from logger.config import setup_logger

logger = setup_logger()

def perform_roomspare_interactions(zipcode):
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--headless=new")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")  # Avoid DevToolsActivePort issue

    
    driver = webdriver.Chrome(options=options)
    try:
        logger.info("Navigating to SpareRoom...")
        driver.get("https://www.spareroom.com/roommates")
        driver.maximize_window()
        
        try:
            zipcode_input = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder='Area or ZIP']"))
            )
            zipcode_input.send_keys(zipcode)
            zipcode_input.send_keys(Keys.ENTER)
            time.sleep(5)
        except Exception as e:
            logger.error(f"Error while entering ZIP code: {e}")
            return None
        
        # Apply price filter
        logger.info("Applying min-max price filter")
        try:
            minprice_input = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="minRent"]'))
            )
            minprice_input.send_keys("200")
            
            maxprice_input = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="maxRent"]'))
            )
            maxprice_input.send_keys("1200")
        except Exception as e:
            logger.error(f"Error while applying price filter: {e}")
        
        # Apply property type filters
        logger.info("Applying property type filters")
        try:
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(2)
            
            one_bed_or_studio = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="searchFilters"]/div/section[6]/div[3]'))
            )
            one_bed_or_studio.click()
            
            whole_properties = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="searchFilters"]/div/section[6]/div[4]'))
            )
            whole_properties.click()
        except Exception as e:
            logger.error(f"Error while applying property type filters: {e}")
        
        # Apply search filter
        logger.info("Applying search filter")
        try:
            driver.execute_script("window.scrollBy(0, 1500);")
            time.sleep(2)
            
            search_filter = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="searchFilters"]/div/div'))
            )
            search_filter.click()
            time.sleep(5)
        except Exception as e:
            logger.error(f"Error while applying search filter: {e}")
        
        # Fetch listings and calculate average price
        logger.info("Fetching listings and calculating average price")
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "listing-card__wrapper"))
            )
            
            listings = driver.find_elements(By.CLASS_NAME, "listing-card__wrapper")
            price_list = []
            
            for listing in listings:
                try:
                    price_per_month = listing.find_element(By.CLASS_NAME, "listing-card__price").text
                    price = price_per_month[:6]

                    cleaned_price = int("".join(i for i in price if i.isdigit()))
                    price_list.append(cleaned_price)
                except Exception as e:
                    logger.warning(f"Skipping listing due to error: {e}")
            
            if price_list:
                average_price = round(sum(price_list) / len(price_list), 3)
                logger.info(f"Average price calculated: {average_price}")
                return average_price
            else:
                logger.warning("No listings found matching the criteria.")
                return None
        except Exception as e:
            logger.error(f"Error occurred while fetching listings: {e}")
            return None
    except Exception as e:
        logger.error(f"Unexpected error while scraping SpareRoom: {e}")
        return None
    finally:
        driver.quit()


