import itertools
import logging

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from include.utils import write_page_source
from include.webdriver import create_web_driver


def real_estate_urls(japan_data: list):
    """
    Extracts real estate data from the given Japan data.

    Args:
        japan_data (list): A list of Japan data containing region and prefecture information.

    Returns:
        list: A list of extracted real estate data.
    """
    urls = []
    classifications = ["mansion", "kodate"]
    conditions = ["shinchiku", "chuko"]
    prefectures = [region["prefecture_en"] for region in japan_data for region in region["prefectures"]]

    # Iterate over property classifications, conditions, and prefectures
    for classification, condition, prefecture in itertools.product(classifications, conditions, prefectures):
        url = f"https://www.homes.co.jp/{classification}/{condition}/{prefecture}/list"

        try:
            # Get real estate URLs
            urls.append(
                {
                    "classification": classification,
                    "condition": condition,
                    "prefecture": prefecture,
                    "real_estate_urls": get_urls_from_all_page_index(url),
                }
            )
        except Exception as e:
            logging.error(f"An error occurred while processing {url}: {e}")

    return urls


def get_urls_from_all_page_index(real_estate_list_url: str):
    """
    Retrieves a list of real estate URLs from the given URL.

    Args:
        url (str): The URL to scrape for real estate URLs.

    Returns:
        list: A list of real estate URLs.
    """
    urls = []

    while True:
        # Create and open a new web driver instance
        web_driver = create_web_driver()
        web_driver.get(real_estate_list_url)

        # Find all real estate elements
        real_estate_divs = web_driver.find_elements(
            By.CSS_SELECTOR,
            "#prg-mod-bukkenList > div.prg-bundle > div.mod-mergeBuilding--sale",
        )
        logging.info(f"Found {len(real_estate_divs)} real estates at {real_estate_list_url}")

        # If no real estates found, write page source to file
        if len(real_estate_divs) == 0:
            write_page_source(real_estate_list_url, web_driver.page_source)

        # Extract real estate URLs
        for real_estate_div in real_estate_divs:
            real_estate_a = real_estate_div.find_element(By.CSS_SELECTOR, "h3.heading > a")
            real_estate_href = real_estate_a.get_attribute("href")
            urls.append(real_estate_href)

        try:
            # Find next page link
            next_page_link = web_driver.find_element(By.CSS_SELECTOR, "li.nextPage > a")
            real_estate_list_url = next_page_link.get_attribute("href")
        except NoSuchElementException:
            break
        finally:
            # Close the web driver
            web_driver.close()
            web_driver.quit()

    return urls
