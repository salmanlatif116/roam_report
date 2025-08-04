import urllib3
import undetected_chromedriver as uc
from selenium.webdriver.common.action_chains import ActionChains
import time
import logging
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from logger.config import setup_logger
logger = setup_logger()


def calculate_rental_revenue(occupancy_str, adr_str):
    try:
        occupancy = float(occupancy_str.strip('%')) / 100
        adr = float(adr_str.strip('$'))
        days_in_month = 20

        # Calculate short-term revenue for 1 month
        short_term = occupancy * adr * days_in_month

        # Apply 15% discount for mid-term (same period, lower rate)
        discount_rate = 0.15
        mid_term = short_term * (1 - discount_rate)

        short_term_revenue = f"${short_term:.2f}"
        mid_term_revenue = f"${mid_term:.2f}"

        logger.info(f"Short term revenue: {short_term_revenue}")
        logger.info(f"Mid term revenue: {mid_term_revenue}")

        return short_term_revenue, mid_term_revenue
    except Exception as e:
        logger.error(f"Error calculating rental revenue: {e}")
        return "N/A", "N/A"


def get_adr_occupancy(address, bedrooms):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    for name in ['selenium', 'seleniumwire', 'urllib3', 'selenium.webdriver.remote.remote_connection']:
        logging.getLogger(name).setLevel(logging.WARNING)

    options = uc.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        f"--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.32 (KHTML, like Gecko) Chrome/{random.randint(90, 120)}.0.0.0 Safari/537.32")

    driver = uc.Chrome(version_main=136, options=options)
    try:
        driver.get("https://rabbu.com/airbnb-calculator")
        time.sleep(random.uniform(3, 7))  # Random delay
        logger.info("navigating to rubbu.com")

        # Scroll and move mouse
        ActionChains(driver).move_by_offset(10, 20).perform()
        driver.execute_script("window.scrollBy(0, 500);")
        from selenium.webdriver.common.keys import Keys
        try:
            wait = WebDriverWait(driver, 10)

            # Wait for address input
            address_input = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//input[@placeholder='Enter an address']"))
            )
            logger.info("address_input found")

            address_input.clear()
            for char in address:
                address_input.send_keys(char)
                time.sleep(0.05)
            logger.info(f"address input sent: {address}")

            # Wait a bit for autocomplete to initialize
            time.sleep(2)

            # Send ARROW_DOWN and ENTER to pick the first suggestion
            address_input.send_keys(Keys.ARROW_DOWN)
            time.sleep(0.5)
            address_input.send_keys(Keys.ENTER)
            logger.info("First address suggestion selected")

            time.sleep(2)

            # Click submit button
            submit_button = wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "button[type='submit']"))
            )
            driver.execute_script(
                "arguments[0].scrollIntoView(true);", submit_button)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", submit_button)
            logger.info("Submit button clicked")

        except Exception as e:
            logger.error(f"Error during address input or submit: {e}")
            
            return "N/A", "N/A"

        try:
            bedrooms_input = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//input[@placeholder='Bedrooms']"))
            )
            logger.info("bedrooms_input found")
        except Exception as e:
            logger.error("Error finding bedrooms input: %s", str(e))

        if bedrooms_input:
            time.sleep(5)
            bedrooms_input.send_keys(bedrooms)
            logger.info(f"{bedrooms} bedrooms input sent")
        # Submit the form
        submit_button = driver.find_element(
            By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        logger.info("submit button clicked")
        time.sleep(3)
        try:
            close_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(@class, 'rounded-full')]"))
            )
            # Scroll into view and click using JavaScript
            driver.execute_script(
                "arguments[0].scrollIntoView(true);", close_button)
            driver.execute_script("arguments[0].click();", close_button)
            logger.info("Successfully clicked close button")
        except Exception as e:
            logger.error(f"Error clicking close button: {e}")
        time.sleep(10)
        try:
            # Wait until at least 2 elements are present
            elements = WebDriverWait(driver, 10).until(
                lambda d: len(d.find_elements(
                    By.XPATH, "//p[contains(@class, 'text-xl') and contains(@class, 'font-bold')]")) >= 2
            )

            # Get all matching <p> elements
            elements = driver.find_elements(
                By.XPATH, "//p[contains(@class, 'text-xl') and contains(@class, 'font-bold')]")

            # Get the 2nd element
            target = elements[1]

            # Get text from it or its <span> if needed
            try:
                occupncy = target.find_element(By.TAG_NAME, "span")
                logger.info(f"occupancy: {occupncy.text}")
            except:
                logger.info(f"occupancy: {target.text}")

        except Exception as e:
            logger.error(f"Error finding occupancy: {e}")
            return "N/A"
        try:
            adr = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="vue-app"]/div/div[3]/div/div/div/div/div[1]/div[2]/div[1]/div/div/div[2]/div/div/div[1]/p[1]/span'))
            )
            logger.info(f" ADR: {adr.text}")
        except Exception as e:
            logger.error(f"Error finding occupancy: {e}")
            return "N/A"
        
        if occupncy and adr:
            return calculate_rental_revenue(occupncy.text, adr.text)
        
        else:
            return f"$0.00", f"$0.00"

    except Exception as e:
        logger.error("Main error: %s", str(e))  

    finally:
        driver.close()



