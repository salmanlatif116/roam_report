
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
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

SCRAPEOPS_API_KEY = '950f2c9a-f6f8-4bf6-805e-a5f895200dab'



def perform_homads_interactions(address):

   
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--window-size=1920x1080')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--blink-settings=imagesEnabled=false')
    # chrome_options.add_argument("--headless")


    # driver = webdriver.Chrome(options=chrome_options)
    driver = webdriver.Chrome(options=chrome_options)
    

    try:
        logger.info("Navigating to Homads calculator...")
        driver.get("https://homads.com/calculator")
        driver.maximize_window()

        time.sleep(10)

        driver.execute_script("window.localStorage.clear();")
        driver.refresh()

        # Wait for address input field
        address_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "input[placeholder='Enter street address']")
            )
        )

        if address_input:
            print(f"fond input..")

        address_input.send_keys(address)
        time.sleep(5)

        # address_input.send_keys(Keys.ENTER)
        # logger.info("waiting for LTM and STR to appear.")
        #
        calculate_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "/html/body/div[1]/div[1]/div[2]/div[2]/button")
            )
        )

        if calculate_btn:
            print(f"calculate btn found")


        calculate_btn.click()

        captcha_code = (
            WebDriverWait(driver, 15)
            .until(EC.element_to_be_clickable((By.XPATH, "//h6[@class='bubble-element Text baToaNaG']"))) 
            .text
        )

        print(captcha_code)

        captcha_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    'body > div.bubble-element.Popup.baToaLaG.bubble-r-container.flex.column > input',
                )
            )
        )
        

        captcha_input.send_keys(captcha_code)
        captcha_process_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "body > div.bubble-element.Popup.baToaLaG.bubble-r-container.flex.column > button")
            )
        )

        captcha_process_btn.click()
        print("Clicked the Verify button.")


        enter_address_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//input[contains(@class, 'bubble-element') and contains(@placeholder, 'street')]",
                )
            )
        )
        

        enter_address_input.send_keys(address)
        submit_address_btn = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "body > div.bubble-element.Popup.baToaOaO.bubble-r-container.flex.column > button")
                )
            )
        
        clicked = submit_address_btn.click()
        if clicked:
            logger.info("submitt btn clicked")

        time.sleep(5)

        try:
            short_term_rental_element = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.XPATH, "/html/body/div[1]/div[2]/div/div/div[1]/div")
                )
            )
            time.sleep(5)
            short_term_rental_items = short_term_rental_element.text
            short_term_rental = short_term_rental_items.split("\n")[0]

        except:
            short_term_rental = "N/A"

        # Wait for Mid-Term Rental Value
        try:
            mid_term_rental_element = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.XPATH, "/html/body/div[1]/div[2]/div/div/div[2]")
                )
            )
            mid_term_rental_items = mid_term_rental_element.text
            mid_term_rental = mid_term_rental_items.split("\n")[0]

        except:
            mid_term_rental = "N/A"
        return short_term_rental, mid_term_rental
    except Exception as e:
        logger.error(f"An error occurred: {e}")

    finally:
        driver.quit()




perform_homads_interactions("1901 Southwood Dr, Baytown, TX 77520")