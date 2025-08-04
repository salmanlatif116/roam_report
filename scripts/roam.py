from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import time
import sys
import json
from selenium.webdriver.common.keys import Keys
import os
import subprocess
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from logger.config import setup_logger

logger = setup_logger()


def perform_roam_interaction():
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--headless")  # Enable if needed
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-webgl")

    driver = webdriver.Chrome(options=options)

    data_list = []
    scraped_hrefs = set()

    try:

        current_page = 1
        while True:
            logger.info("Navigating to the WithRoam.")
            driver.get(
                f"https://www.withroam.com/state/TX?down_payment=100000&max_list_price=500000&max_price=2000&page={current_page}&va=true"
            )
            driver.maximize_window()
            driver.implicitly_wait(30)
            logger.info(f"Scraping listings from the page: {current_page}")

            listing_elements = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located(
                    (
                        By.XPATH,
                        '//div[starts-with(@id, "map-card-sidebar-card-")]//a[contains(@href, "/listing/")]',
                    )
                )
            )

            hrefs = list(
                set(
                    el.get_attribute("href")
                    for el in listing_elements
                    if el.get_attribute("href")
                )
            )
            hrefs = [href for href in hrefs if href not in scraped_hrefs]

            logger.info(f"Retrieved {len(hrefs)} unique listings on this page.")
            if len(hrefs) == 0:
                logger.info(
                    f"No listings found on page {current_page}. Assuming last page reached."
                )
                break

            for href in hrefs:
                logger.info(f"Processing listing {href}")
                scraped_hrefs.add(href)

                driver.execute_script(f"window.open('{href}', '_blank');")
                driver.switch_to.window(driver.window_handles[-1])

                try:

                    square_feet = (
                        WebDriverWait(driver, 10)
                        .until(
                            EC.visibility_of_element_located(
                                (
                                    By.XPATH,
                                    '//*[@id="main"]/div[3]/div[2]/div[1]/p[2]/span[3]',
                                )
                            )
                        )
                        .text.replace(",", "")
                    )

                    square_feet = "".join(i for i in square_feet if i.isdigit())

                    property_type = (
                        WebDriverWait(driver, 10)
                        .until(
                            EC.presence_of_element_located(
                                (
                                    By.XPATH,
                                    '//*[@id="main"]/div[3]/div[2]/div[1]/div[4]/div[3]',
                                )
                            )
                        )
                        .text
                    )

                    print(f"property type: {property_type}")

                    loan_detail_section = (
                        WebDriverWait(driver, 10)
                        .until(
                            EC.presence_of_element_located(
                                (
                                    By.XPATH,
                                    '//*[@id="main"]/div[3]/div[2]/div[1]/div[8]',
                                )
                            )
                        )
                        .text
                    )

                    remaining_loan_term = None
                    loan_lines = loan_detail_section.split("\n")
                    for i in range(len(loan_lines)):
                        if "Remaining term" in loan_lines[i]:
                            remaining_loan_term = loan_lines[i + 1]
                            break

                    print(f"remaining loan term: {remaining_loan_term}")

                    address_first_half = (
                        WebDriverWait(driver, 10)
                        .until(
                            EC.presence_of_element_located(
                                (
                                    By.XPATH,
                                    '//*[@id="main"]/div[3]/div[2]/div[1]/div[1]',
                                )
                            )
                        )
                        .text
                    )

                    address_second_half = (
                        WebDriverWait(driver, 10)
                        .until(
                            EC.presence_of_element_located(
                                (By.XPATH, '//*[@id="main"]/div[3]/div[2]/div[1]/p[1]')
                            )
                        )
                        .text
                    )

                    address = f"{address_first_half} {address_second_half}"

                    print(f"address: {address}")

                    list_price = (
                        WebDriverWait(driver, 10)
                        .until(
                            EC.presence_of_element_located(
                                (
                                    By.XPATH,
                                    '//*[@id="main"]/div[3]/div[2]/div[1]/div[2]/h4',
                                )
                            )
                        )
                        .text
                    )

                    interest_rate = (
                        WebDriverWait(driver, 10)
                        .until(
                            EC.presence_of_element_located(
                                (
                                    By.XPATH,
                                    '//span[@class="fw-600 text-primary font-number"]',
                                )
                            )
                        )
                        .text
                    )

                    print(f"interest_rate: {interest_rate}")
                    payment_detail_section = (
                        WebDriverWait(driver, 10)
                        .until(
                            EC.presence_of_element_located(
                                (
                                    By.XPATH,
                                    '//*[@id="main"]/div[3]/div[2]/div[1]/div[7]',
                                )
                            )
                        )
                        .text
                    )

                    principal_and_interest = None
                    payment_lines = payment_detail_section.split("\n")
                    for i in range(len(payment_lines)):
                        if "Principal & interest" in payment_lines[i]:
                            principal_and_interest = payment_lines[i + 1]
                            break

                    down_payment_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (
                                By.XPATH,
                                '//input[@name="short_listed_home[down_payment]"]',
                            )
                        )
                    )

                    down_payment = down_payment_element.get_attribute("value")
                    print(f"down_payment: {down_payment}")

                    # # # Loan term conversion
                    # match = re.search(r"(\d+)\s*yrs?\s*and\s*(\d+)\s*mos?", remaining_loan_term)
                    # if match:
                    #     years = int(match.group(1))
                    #     months = int(match.group(2))
                    #     loan_term_months = years * 12 + months
                    # else:
                    #     logger.warning("Invalid loan term format.")
                    #     loan_term_months = 360  # default fallback

                    # # Clean and compute values
                    # cleaned_list_price = int("".join(i for i in list_price if i.isdigit()))
                    # cleaned_interest_rate = float(
                    #     "".join(i for i in interest_rate if i.isdigit())[0:2]) / 10
                    # cleaned_principal_and_interest = int("".join(i for i in principal_and_interest if i.isdigit()))

                    # down_payment = calculate_down_payment(
                    #     cleaned_list_price,
                    #     cleaned_interest_rate,
                    #     cleaned_principal_and_interest,
                    #     loan_term_months,
                    # )
                    zipcode = address[-5:]
                    bedrooms_string = (
                        WebDriverWait(driver, 10)
                        .until(
                            EC.presence_of_element_located(
                                (
                                    By.XPATH,
                                    '//*[@id="main"]/div[3]/div[2]/div[1]/p[2]/span[1]',
                                )
                            )
                        )
                        .text
                    )
                    bedrooms = int(bedrooms_string[0])
                    address_for_smtr = address + ", USA"

                    data = {
                        "address": address,
                        "listing_price": list_price,
                        "down_payment": str(down_payment),
                        "principal_and_interest": principal_and_interest,
                        "interest_rate": interest_rate,
                        "property_type": property_type,
                        "formatted_address": address_for_smtr,
                        "num_of_beds": bedrooms,
                        "zipcode": zipcode,
                        "square_feet": square_feet,
                    }

                    data_list.append(data)
                    with open("roam_data.json", "w") as file:
                        json.dump(data_list, file, indent=4)

                    logger.info(f"Data scraped: {data}")

                except Exception as e:
                    logger.error(f"Error scraping listing {href}: {e}")

                finally:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    time.sleep(3)

            current_page += 1


    except Exception as e:
        try:
            driver.get_screenshot_as_file("error_screenshot.png")
        except Exception as ss_err:
            logger.error(f"Failed to take screenshot: {ss_err}")
        logger.error(f"An error occurred: {e}")

    finally:
        driver.quit()

    return data_list


def calculate_down_payment(property_price, interest_rate, monthly_pi, loan_term_months):
    r = (interest_rate / 100) / 12
    n = loan_term_months

    if r == 0:
        loan_amount = monthly_pi * n
    else:
        loan_amount = monthly_pi * (1 - (1 + r) ** -n) / r

    down_payment = property_price - loan_amount
    return round(max(down_payment, 0), 2)


perform_roam_interaction()
