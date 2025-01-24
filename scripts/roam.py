from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import time
import sys
import json
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from logger.config import setup_logger

logger = setup_logger()

def perform_web_interaction():
    options = webdriver.ChromeOptions()
    options.add_argument('--window-size=1920x1080')
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')

    driver = webdriver.Chrome(options=options)

    data_list = []

    try:
        logger.info("Navigating to the 'https://www.withroam.com/state/TX'.")
        driver.get('https://www.withroam.com/state/TX?down_payment=50000&max_price=2000&va=true')
        driver.maximize_window()
        driver.implicitly_wait(30)

        while True:
            # Scrape data from the current page
            logger.info("Scraping listings from the current page.")
            listings = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.XPATH, '//a[contains(@class, "text-black") and contains(@href, "/listing/") and not(.//div[contains(@class, "boost-badge")]) ]'))
            )
            logger.info(f"Retrieved {len(listings)} listings on this page.")

            for index, listing in enumerate(listings):
                try:
                    logger.info(f"Processing listing {index + 1}")

                    # Refresh the listings due to potential stale element issues
                    listings = WebDriverWait(driver, 20).until(
                        EC.presence_of_all_elements_located((By.XPATH, '//a[contains(@class, "text-black") and contains(@href, "/listing/") and not(.//div[contains(@class, "boost-badge")]) ]'))
                    )
                    current_listing = listings[index]

                    # Scroll into view and click
                    driver.execute_script("arguments[0].scrollIntoView(true);", current_listing)
                    time.sleep(2)
                    driver.execute_script("arguments[0].click();", current_listing)

                    # Wait for the new tab to open
                    WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
                    driver.switch_to.window(driver.window_handles[-1])

                    # Scrape data from the new tab
                    address = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//h1[@class="fs-14 text-5e fw-bold"]'))
                    ).text
                    list_price = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/div[4]/div/div[2]/div/div/div[2]/div/div[1]/div[2]'))
                    ).text
                    down_payment = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/div[4]/div/div[2]/div/div/div[2]/div/div[2]/div[2]'))
                    ).text
                    interest_rate = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/div[4]/div/div[2]/div/div/div[1]/div[1]/div[1]/div[3]'))
                    ).text
                    principal_and_interest = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/div[4]/div/div[2]/div/div/div[1]/div[1]/div[2]/div[3]'))
                    ).text

                    data = {
                        "address": address,
                        "listing_price": list_price,
                        "down_payment": down_payment,
                        "principal_and_interest": principal_and_interest,
                        "interest_rate": interest_rate,
                    }
                    with open("roam_data.json", "w") as file:
                        data_list.append(data)
                        json.dump(data_list, file, indent=4)
                    logger.info(f"Data scraped: {data}")

                except Exception as e:
                    logger.error(f"Error scraping listing {index + 1}: {e}")

                finally:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    time.sleep(5)

            
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/div[1]/div[4]/div[1]/div/div[3]/a[9]'))
                    
                )
                if "disabled" in next_button.get_attribute("class"):
                    logger.info("Reached the last page. Exiting pagination loop.")
                    break
                
                driver.execute_script("arguments[0].click();", next_button)
                logger.info("Navigating to the next page.")
                time.sleep(5)
            except TimeoutException:
                logger.info("No 'Next' button found. Exiting pagination loop.")
                break


    except Exception as e:
        driver.save_screenshot("error_screenshot.png")
        logger.error(f"An error occurred: {e}")
    finally:
        driver.quit()

    return data_list

