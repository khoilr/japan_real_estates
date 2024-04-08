import logging

import requests
from bs4 import BeautifulSoup

from real_estates.utils import write_page_source


def regions_and_prefectures():
    """
    Extracts regions and prefectures data from a website.
    Returns a list of dictionaries containing region and prefecture information.
    """

    # Create an empty list to store the data
    japan_data = []

    try:
        # Fetch the HTML content
        url = "https://www.homes.co.jp/mansion/shinchiku/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Parse HTML content with BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")

        # Find all the regions
        region_uls = soup.select("div#selectArea > ul")

        # Iterate over each region
        for region_ul in region_uls:
            # Get the class attribute of the region
            region_class = region_ul.get("class")

            # Check if the region has a class attribute
            if region_class:
                # Get the region name
                region_name = region_class[0]  # Assuming class attribute has only one class

                # Find all the prefectures in the region
                prefecture_lis = region_ul.find_all("li")

                # Iterate over each prefecture
                for prefecture_li in prefecture_lis:
                    # Get the English name of the prefecture from class attribute
                    prefecture_en = prefecture_li.get("class")[0]  # Assuming class attribute has only one class

                    # Get the Japanese name of the prefecture
                    prefecture_jp = prefecture_li.text.strip()

                    japan_data.append(
                        {
                            "region": region_name,
                            "prefecture_en": prefecture_en,
                            "prefecture_jp": prefecture_jp,
                        }
                    )

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        # Optionally, write the page source to file for debugging
        write_page_source(url.replace("/", "-"), response.content)

    # Return the Japan data
    return japan_data
