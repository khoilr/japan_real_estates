import itertools
import logging

import trio
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from include.utils import create_web_driver_trio, write_page_source

urls = []


def real_estate_urls(japan_data: list):
    trio.run(_real_estate_urls, japan_data)

    return urls


async def _real_estate_urls(japan_data: list):
    classifications = ["mansion", "kodate"]
    conditions = ["shinchiku", "chuko"]
    prefectures = [region["prefecture_en"] for region in japan_data for region in region["prefectures"]]

    limiter = trio.CapacityLimiter(8)

    async with trio.open_nursery() as nursery:
        # Iterate over property classifications, conditions, and prefectures
        for classification, condition, prefecture in itertools.product(classifications, conditions, prefectures):
            url = f"https://www.homes.co.jp/{classification}/{condition}/{prefecture}/list"
            nursery.start_soon(
                get_urls_from_all_page_index,
                {"url": url, "classification": classification, "condition": condition, "prefecture": prefecture},
                limiter,
            )

    return urls


async def get_urls_from_all_page_index(real_estate_list_url: dict, limiter: trio.CapacityLimiter):
    url = real_estate_list_url["url"]
    classification = real_estate_list_url["classification"]
    condition = real_estate_list_url["condition"]
    prefecture = real_estate_list_url["prefecture"]

    async with limiter:
        while True:
            try:
                # Create and open a new web driver instance
                web_driver = await create_web_driver_trio()
                web_driver.get(url)

                # Find all real estate elements
                real_estate_divs = web_driver.find_elements(
                    By.CSS_SELECTOR,
                    "#prg-mod-bukkenList > div.prg-bundle > div.mod-mergeBuilding--sale",
                )
                logging.info(f"Found {len(real_estate_divs)} real estates at {url}")

                # If no real estates found, write page source to file
                if len(real_estate_divs) == 0:
                    write_page_source(url, web_driver.page_source)

                # Extract real estate URLs
                for real_estate_div in real_estate_divs:
                    real_estate_a = real_estate_div.find_element(By.CSS_SELECTOR, "h3.heading > a")
                    real_estate_href = real_estate_a.get_attribute("href")
                    urls.append(
                        {
                            "classification": classification,
                            "condition": condition,
                            "prefecture": prefecture,
                            "real_estate_urls": real_estate_href,
                        }
                    )

                try:
                    # Find next page link
                    next_page_link = web_driver.find_element(By.CSS_SELECTOR, "li.nextPage > a")
                    url = next_page_link.get_attribute("href")
                except NoSuchElementException:
                    break
                finally:
                    # Close the web driver
                    web_driver.close()
                    web_driver.quit()

            except Exception as e:
                logging.error(f"An error occurred: {str(e)}")
                break
