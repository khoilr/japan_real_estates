import itertools
import logging

from airflow.providers.mongo.hooks.mongo import MongoHook
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from include.webdriver import create_web_driver


def real_estates(japan_data: list):
    extracted_data = []
    property_classifications = ["mansion", "kodate"]
    property_conditions = ["shinchiku", "chuko"]
    prefectures = [region["prefecture_en"] for region in japan_data for region in region["prefectures"]]

    mongo_hook = MongoHook(mongo_conn_id="mongo")
    mongo_client = mongo_hook.get_conn()
    db = mongo_client.db
    db.japanese.create_index({"url": 1}, unique=True)

    for classification, condition, prefecture in itertools.product(
        property_classifications, property_conditions, prefectures
    ):
        url = f"https://www.homes.co.jp/{classification}/{condition}/{prefecture}/list"

        try:
            real_estate_urls = get_real_estate_urls(url)
            for real_estate_url in real_estate_urls:
                extracted_info = extract_and_store_real_estate_data(db, real_estate_url)
                if extracted_info:
                    extracted_data.append(extracted_info)
        except Exception as e:
            logging.error(f"An error occurred while processing {url}: {e}")

    logging.info(f"Extracted {len(extracted_data)} real estates")
    return extracted_data


def extract_real_estate_from_table(table_element: WebElement):
    """
    Extracts real estate data from a table element.

    Args:
        table_element (WebElement): The table element containing the real estate data.

    Returns:
        dict: A dictionary containing the extracted real estate data, where the keys are the table row headers
              and the values are the corresponding row values.
    """
    # Initialize an empty dictionary to store the extracted data
    extracted_data = {}

    # Find all rows in the table
    rows = table_element.find_elements(By.CSS_SELECTOR, "tbody > tr")

    # Process each row
    for row in rows:
        # Extract the key and value from each row
        key_element = row.find_element(By.CSS_SELECTOR, "th")
        value_element = row.find_element(By.CSS_SELECTOR, "td")
        key = key_element.text
        value = value_element.text

        # Store the extracted data in the dictionary
        extracted_data[key] = value

    # Return the extracted data
    return extracted_data


def get_real_estate_urls(url: str):
    real_estate_urls = []

    while True:
        web_driver = create_web_driver()
        web_driver.get(url)

        real_estates = web_driver.find_elements(
            By.CSS_SELECTOR,
            "#prg-mod-bukkenList > div.prg-bundle > div.mod-mergeBuilding--sale",
        )
        logging.info(f"Found {len(real_estates)} real estates at {url}")

        if len(real_estates) == 0:
            write_page_source(url, web_driver.page_source)

        for real_estate in real_estates:
            real_estate_a = real_estate.find_element(By.CSS_SELECTOR, "h3.heading > a")
            real_estate_href = real_estate_a.get_attribute("href")
            real_estate_urls.append(real_estate_href)

        try:
            next_page_link = web_driver.find_element(By.CSS_SELECTOR, "li.nextPage > a")
            url = next_page_link.get_attribute("href")
        except NoSuchElementException:
            break
        finally:
            web_driver.close()
            web_driver.quit()

    return real_estate_urls


def write_page_source(url: str, page_source: str):
    with open(f"outputs/error_{url.replace('/', '_').replace(':', '')}.html", "w") as f:
        f.write(page_source)


def extract_and_store_real_estate_data(db, real_estate_url):
    if db.japanese.find_one({"url": real_estate_url}):
        logging.info(f"Skipping {real_estate_url} - URL already exists")
        return None

    extracted_info = extract_real_estate_data(real_estate_url)
    if extracted_info:
        extracted_info["url"] = real_estate_url
        db.japanese.insert_one(extracted_info)
        logging.info(f"Inserted {extracted_info['_id']}")
        return extracted_info
    else:
        logging.warning(f"Failed to extract data from {real_estate_url}")
        return None


def extract_real_estate_data(real_estate_url: str):
    # Initialize an empty dictionary to store the extracted data
    data = {}

    # Create a new web driver instance and open the URL
    web_driver = create_web_driver()
    web_driver.get(real_estate_url)

    try:
        # Extract data from seller overview table
        seller_overview_table = web_driver.find_element(By.CSS_SELECTOR, "h3#outline_salesOverview ~ div > table")
        data.update(extract_real_estate_from_table(seller_overview_table))

        # Extract data from general overview table
        general_overview_table = web_driver.find_element(By.CSS_SELECTOR, "h3#outline_generalOverview ~ div > table")
        data.update(extract_real_estate_from_table(general_overview_table))

    except NoSuchElementException:
        logging.error("Exception occurred", exc_info=True)
        logging.warning(real_estate_url)
        logging.warning(web_driver.page_source)

    # Close the web driver
    web_driver.close()
    web_driver.quit()

    # Return the extracted data
    return data
