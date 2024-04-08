import asyncio
import logging
from datetime import datetime
from urllib.parse import urlparse

import aiohttp
from bs4 import BeautifulSoup
from real_estates.utils import write_page_source

BATCH_SIZE = 10000


async def _extract_real_estate_urls():
    """
    Extracts real estate URLs from the homes.co.jp website.

    Returns:
        list: A list of real estate URLs.
    """
    urls = []

    payload = "cond%5Bnewdate%5D=1"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    }

    async with aiohttp.ClientSession() as session:
        # Fetch the initial page
        response_text = await fetch("https://www.homes.co.jp/list/", headers, payload, session)
        soup = BeautifulSoup(response_text, "html.parser")

        # Get the total number of real estates
        total_num_span = soup.select_one("span.totalNum")
        total_num = int(total_num_span.text.replace(",", "")) if total_num_span else 0
        logging.info(f"Found {total_num} real estates")

        # Get the last page number
        last_page_li = soup.select_one("#searchResult li.lastPage")
        # Todo: Get actual number of pages
        last_page = 30 if last_page_li else 1
        # last_page = int(last_page_li.text) if last_page_li else 1
        logging.info(f"Found {last_page} pages")

        # Calculate the number of batches
        batch_count = (last_page + BATCH_SIZE - 1) // BATCH_SIZE

        # Iterate over each batch
        for batch_index in range(batch_count):
            # Create a list of tasks to fetch the pages in the current batch
            tasks = [
                fetch(f"https://www.homes.co.jp/list/?page={i}", headers, payload, session)
                for i in range(1 + batch_index * BATCH_SIZE, min((batch_index + 1) * BATCH_SIZE + 1, last_page + 1))
            ]
            responses = await asyncio.gather(*tasks)

            logging.info(f"Batch {batch_index + 1}/{batch_count} fetched {len(responses)} pages")

            # Extract URLs from each response and add them to the list
            for index, response_text in enumerate(responses):
                urls.extend(await extract_urls_at_page(response_text, batch_index * BATCH_SIZE + index + 1))

    # Filter out URLs that type of real estate is Chintai
    urls = list(filter(lambda x: x["type"] != "chintai", urls))

    logging.info(f"Extracted {len(urls)} URLs")

    return urls


async def fetch(url: str, headers: dict, payload: str, session: aiohttp.ClientSession):
    """
    Fetches the content of a given URL using a POST request.

    Args:
        url (str): The URL to fetch the content from.
        headers (dict): The headers to include in the request.
        payload (str): The payload to include in the request.
        session (aiohttp.ClientSession): The aiohttp client session to use for the request.

    Returns:
        str: The text content of the response.

    Raises:
        Any exceptions raised by the aiohttp library.
    """
    async with session.request("POST", url, data=payload, headers=headers) as response:
        return await response.text()


async def extract_urls_at_page(response_text: str, index: int):
    """
    Extracts URLs of real estate listings from the given response text.

    Args:
        response_text (str): The HTML response text of the page.
        index (int): The index of the page.

    Returns:
        list: A list of dictionaries containing the extracted URLs.
              Each dictionary has a single key-value pair where the key is "url" and the value is the extracted URL.
    """
    urls = []

    soup = BeautifulSoup(response_text, "html.parser")
    real_estate_divs = soup.select(
        "#prg-mod-bukkenList > div.prg-bundle > div.mod-mergeBuilding--sale, #prg-mod-bukkenList > div.prg-bundle > div.mod-mergeBuilding--rent--photo"
    )

    if not real_estate_divs:
        write_page_source(f"https://www.homes.co.jp/list?page={index}".replace("/", "-"), soup.prettify())
        logging.warning(f"No real estate divs found on page {index}")

    for real_estate_div in real_estate_divs:
        real_estate_a = real_estate_div.select_one(".heading > a")
        if real_estate_a and "href" in real_estate_a.attrs:
            url = real_estate_a["href"]
            url_obj = urlparse(url)
            urls.append({"url": url, "type": url_obj.path.split("/")[1], "created_at": datetime.now()})

    return urls
