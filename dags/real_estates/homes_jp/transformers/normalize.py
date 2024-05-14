import logging
import re

import trio


async def _normalize(data: list):
    normalized_data = []

    async with trio.open_nursery() as nursery:
        for item in data:
            nursery.start_soon(normalize, item, normalized_data)

    logging.info(f"Normalized {len(normalized_data)} items")

    return normalized_data


async def normalize(item: dict, normalized_data: list):
    normalized_item = {}

    building_area = re.sub(
        r"\(.*?\)|\（.*?\）",
        "",
        item["building_area"].replace(",", "").replace("m2", "").replace("ｍ2", ""),
    )
    building_area_bound = re.findall(r"\d+\.\d+|\d+", building_area)
    if len(building_area_bound) == 2:
        normalized_item["min_building_area"] = float(building_area_bound[0])
        normalized_item["max_building_area"] = float(building_area_bound[1])
    else:
        normalized_item["building_area"] = float(building_area_bound[0])

    try:
        land_area = re.sub(
            r"\(.*?\)|\（.*?\）", "", item["land_area"].replace(",", "").replace("m2", "").replace("ｍ2", "")
        )
        land_area_bound = re.findall(r"\d+\.\d+|\d+", land_area)
        if not land_area_bound:
            normalized_item["land_area"] = 0
        if len(land_area_bound) == 2:
            normalized_item["min_land_area"] = float(land_area_bound[0])
            normalized_item["max_land_area"] = float(land_area_bound[1])
        else:
            logging.warning(item["land_area"])
            normalized_item["land_area"] = float(land_area_bound[0])
    except Exception as e:
        logging.error("Error extracting land area ({}): {}".format(item["land_area"], e))

    price = re.sub(r"\(.*?\)|\（.*?\）", "", item["price"].replace("万円", "").replace(",", ""))
    price_bound = re.findall(r"\d+\.\d+|\d+", price)
    if not price_bound:
        normalized_item["price"] = 0
    elif len(price_bound) == 2:
        normalized_item["min_price"] = float(price_bound[0])
        normalized_item["max_price"] = float(price_bound[1])
    else:
        normalized_item["price"] = float(price_bound[0])

    normalized_item["address"] = re.sub(r"\(.*?\)|\（.*?\）", "", item["address"])
    normalized_item["language"] = "JP"

    normalized_data.append({**item, **normalized_item})
