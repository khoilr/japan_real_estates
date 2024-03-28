import logging

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from include.utils import create_web_driver


def real_estates(urls: list):
    """
    Extracts real estate data from the given Japan data.

    Args:
        japan_data (list): A list of Japan data containing region and prefecture information.

    Returns:
        list: A list of extracted real estate data.
    """
    extracted_data = []

    # Iterate over property classifications, conditions, and prefectures
    for url_dict in urls:
        url = url_dict["url"]

        try:
            extracted = extract_real_estate_data(url)
            if extracted:
                extracted.update(url)
                extracted_data.append(extracted)

        except Exception as e:
            logging.error(f"An error occurred while processing {url}: {e}")

    logging.info(f"Extracted info from {len(extracted_data)} real estates")
    return extracted_data


def extract_real_estate_data(real_estate_url: str):
    """
    Extracts real estate data from the given real estate URL.

    Args:
        real_estate_url (str): The URL of the real estate.

    Returns:
        dict: A dictionary containing the extracted real estate data, where the keys are the table row headers
              and the values are the corresponding row values.
    """
    # Initialize an empty dictionary to store the extracted data
    extracted_data = {}

    # Create a new web driver instance and open the URL
    web_driver = create_web_driver()
    web_driver.get(real_estate_url)

    try:
        description_element = web_driver.find_element(By.CSS_SELECTOR, "#feature h1").text.strip()
        extracted_data["description"] = description_element

        image_element = web_driver.find_element(
            By.CSS_SELECTOR,
            "ol[data-pages--detail--sbmansion--pc--photo_slider-target='photoList'] > li img",
        )
        image_url = image_element.get_attribute("src")
        extracted_data["image_url"] = image_url

        # Extract data from seller overview table
        seller_overview_table = web_driver.find_element(By.CSS_SELECTOR, "h3#outline_salesOverview ~ div > table")
        extracted_data.update(extract_data_from_table(seller_overview_table))

        # Extract data from general overview table
        general_overview_table = web_driver.find_element(By.CSS_SELECTOR, "h3#outline_generalOverview ~ div > table")
        extracted_data.update(extract_data_from_table(general_overview_table))

    except NoSuchElementException as e:
        logging.error(f"An exception occurred while extracting real estate data from {real_estate_url}, {e.msg}")

    # Close the web driver
    web_driver.close()
    web_driver.quit()

    # Return the extracted data
    return extracted_data


def extract_data_from_table(table_element: WebElement):
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
