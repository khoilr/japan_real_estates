import logging
from pprint import pformat

from selenium.webdriver.common.by import By

from include.webdriver import create_web_driver


def regions_and_prefectures():
    """
    Extracts regions and prefectures data from a website.
    Returns a list of dictionaries containing region and prefecture information.
    """

    # Create an empty list to store the data
    japan_data = []

    # Create a web driver instance
    web_driver = create_web_driver()

    # Open the URL
    web_driver.get("https://www.homes.co.jp/mansion/shinchiku/")

    # Find all the regions
    region_elements = web_driver.find_elements(by=By.CSS_SELECTOR, value="div#selectArea > ul")

    # Iterate over each region
    for region_element in region_elements:
        # Get the class attribute of the region
        region_class = region_element.get_attribute("class")

        # Check if the region has a class attribute
        if region_class:
            # Get the region name
            region_name = region_class

            # Find all the prefectures in the region
            prefecture_elements = region_element.find_elements(by=By.TAG_NAME, value="li")

            # Create an empty list to store the prefectures
            prefectures = []

            # Iterate over each prefecture
            for prefecture_element in prefecture_elements:
                # Get the class attribute of the prefecture
                prefecture_class = prefecture_element.get_attribute("class")

                # Check if the prefecture has a class attribute
                if prefecture_class:
                    # Get the English and Japanese names of the prefecture
                    prefecture_en = prefecture_class
                    prefecture_jp = prefecture_element.text

                    # Append the prefecture data to the list
                    prefectures.append(
                        {
                            "prefecture_en": prefecture_en,
                            "prefecture_jp": prefecture_jp,
                        }
                    )

            # Append the region data to the list
            japan_data.append(
                {
                    "region": region_name,
                    "prefectures": prefectures,
                }
            )

    # Terminate the web driver
    web_driver.close()
    web_driver.quit()

    # Log the extracted data
    logging.info(pformat(japan_data))

    # Return the Japan data
    return japan_data
