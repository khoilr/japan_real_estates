import asyncio
import logging

import aiohttp
from bs4 import BeautifulSoup, Tag

import yarl

BATCH_SIZE = 10000


# This function is responsible for extracting real estate data from a list of URLs.
async def _extract_real_estates(urls):
    real_estates = []

    # Set the headers for the HTTP requests
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }

    # Calculate the number of batches based on the batch size
    batch_count = (len(urls) + BATCH_SIZE - 1) // BATCH_SIZE

    # Create a new aiohttp client session
    async with aiohttp.ClientSession() as session:
        # Iterate over each batch
        for batch_index in range(batch_count):
            # Create a list of tasks for fetching the URLs in the current batch
            tasks = [
                fetch(url["url"], headers, session)
                for url in urls[batch_index * BATCH_SIZE : (batch_index + 1) * BATCH_SIZE]
            ]
            # Use asyncio.gather to concurrently fetch the URLs in the current batch
            responses = await asyncio.gather(*tasks)

            # Log the number of pages fetched in the current batch
            logging.info(f"Batch {batch_index + 1}/{batch_count} fetched {len(responses)} pages")

            # Process each response and extract the real estate data
            for response_text, url_obj in responses:
                real_estate_data = await extract_real_estate_data(response_text, url_obj)
                # Append the real estate data to the list if it is not None
                real_estates.append({**real_estate_data}) if real_estate_data else None

    # Log the number of real estate data extracted
    logging.info(f"Extracted {len(real_estates)} real estates")

    # Return the list of extracted real estate data
    return real_estates


async def fetch(url: str, headers: dict, session: aiohttp.ClientSession):
    """
    Fetches the content of a given URL using a POST request.

    Args:
        url (str): The URL to fetch the content from.
        headers (dict): The headers to include in the request.
        session (aiohttp.ClientSession): The aiohttp client session to use for the request.

    Returns:
        str: The text content of the response.

    Raises:
        Any exceptions raised by the aiohttp library.
    """
    async with session.request("GET", url, headers=headers) as response:
        return (await response.text(), response.url_obj)


async def extract_real_estate_data(response_text: str, url_obj: yarl.URL):
    url_human = url_obj.human_repr()
    soup = BeautifulSoup(response_text, "html.parser")

    try:
        # Not found
        if soup.select_one("#contents div.mod-bukkenNotFound"):
            logging.warning(f"Real estate not found: {url_human}")
            return None

        name = soup.select_one("h1 span.bukkenName")
        if name:
            return {**format_1(soup), "url": url_human, "format": 1}

        # name = soup.select_one("div[data-component='ArticleHeader'] h1 > span:last-child")
        # if name:
        #     return {**format_2(soup), "url": url_human, "format": 2}

        logging.warning(f"{url_human} doesn't match any type of format. Skipping...")

        # name = soup.select_one("h1 > span#chk-bkh-name")
        # if name:
        #     logging.warning(f"Temporarily skipping {url_human}")
        #     return None

    except Exception as e:
        logging.error(f"Error extracting data from {url_human}: {e}")
        return None

    # logging.warning(f"Could not extract data from {url_human}")
    return None


def format_1(soup: BeautifulSoup):
    real_estate_data = {}

    # Get name
    name = soup.select_one("h1 span.bukkenName").text.strip()
    real_estate_data["name"] = name

    # Get images
    image_elements = soup.select(".galleryTop .photoSlide")
    real_estate_data["images"] = [image_element["data-image"] for image_element in image_elements]

    # Get price
    price = soup.select_one("#prg-bukkenDetailHeader > div.propertyInfo dl.price > dd > span").text.strip()
    real_estate_data["price"] = price

    # Get address
    address = soup.select_one("#prg-bukkenDetailHeader > div.propertyInfo > div:nth-child(2) > dl > dd").text.strip()
    real_estate_data["address"] = address

    # Get traffics
    traffics = soup.select(".trafficText")
    real_estate_data["traffics"] = [traffic.text.strip() for traffic in traffics]

    # Get land area
    land_area = soup.select_one("#prg-bukkenDetailHeader > div.propertyInfo > div:nth-child(4) > dl:nth-child(1) > dd")
    real_estate_data["land_area"] = land_area.text.strip()

    # Get building area
    building_area = soup.select_one(
        "#prg-bukkenDetailHeader > div.propertyInfo > div:nth-child(4) > dl:nth-child(2) > dd"
    )
    real_estate_data["building_area"] = building_area.text.strip()

    # Get floor plan
    float_plan = soup.select_one("#prg-bukkenDetailHeader > div.propertyInfo > div:nth-child(4) > dl:nth-child(3) > dd")
    real_estate_data["floor_plan"] = float_plan.text.strip()

    return real_estate_data


def format_2(soup):
    def extract_from_table(table: Tag):
        real_estate_data = {}

        trs = table.select("tbody > tr")

        for tr in trs:
            key = tr.select_one("th").text.strip()
            value = " ".join(value.text.strip() for value in tr.select("td > p"))
            real_estate_data[key] = value

        return real_estate_data

    real_estate_data = {}

    # Get name
    name = soup.select_one("div[data-component='ArticleHeader'] h1 > span:last-child").text.strip()
    real_estate_data["name"] = name

    # Get images
    image_elements = soup.select('photo-slider photo-slider-photo img[data-targets="photo-slider.images"]')
    real_estate_data["images"] = [image_element["src"] for image_element in image_elements]

    # Get overview
    table = soup.select_one("#about table")
    real_estate_data.update(extract_from_table(table))

    return real_estate_data
