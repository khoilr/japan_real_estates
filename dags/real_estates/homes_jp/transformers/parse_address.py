import logging

import trio
from japanese_address import parse

japanese_to_english = {
    "借地権の種類・期間": "Type and duration of land lease rights",
    "取引態様": "Transaction method",
    "国土法": "National Land Law",
    "土地面積": "Land area",
    "建物構造": "Building structure",
    "建築確認番号": "Building confirmation number",
    "引き渡し可能年月": "Delivery availability date",
    "最多価格帯": "Highest price range",
    "機構融資": "Institutional financing",
    "次回更新予定日": "Next update scheduled date",
    "道路の幅員": "Road width",
    "都市計画": "Urban planning",
    "主たる設備の概要": "Overview of main facilities",
    "交通": "Transportation",
    "備考": "Remarks",
    "取引条件有効期限": "Validity period of transaction conditions",
    "土地の権利": "Land rights",
    "地目": "Land category",
    "売主": "Seller",
    "完成予定日": "Expected completion date",
    "建物面積": "Building area",
    "情報更新日": "Information update date",
    "所在地": "Location",
    "施工会社": "Construction company",
    "用途地域": "Land use zone",
    "販売スケジュール": "Sales schedule",
    "販売価格": "Selling price",
    "販売戸数 / 総戸数": "Number of units for sale / Total units",
    "間取り": "Floor plan",
    "駐車場": "Parking lot",
    "保証金": "Security deposit",
    "借地権の月賃料": "Monthly land lease fee",
    "建ぺい率・容積率": "Building coverage ratio and floor area ratio",
    "開発許可番号": "Development permit number",
    "建築条件": "Building conditions",
    "販売区画数 / 総区画数": "Number of units for sale / Total units",
    "造成完了予定日": "Scheduled completion date of development",
    "開発面積": "Development area",
    "その他費用": "Other expenses",
    "モデルルーム情報": "Model room information",
    "イベント情報": "Event information",
    "予定最多価格帯": "Planned highest price range",
}


async def _transform_parse_address(data):
    parsed_data = []

    async with trio.open_nursery() as nursery:
        for item in data:
            nursery.start_soon(parse_address, item, item["address"], parsed_data)

    logging.info(f"Parsed {len(parsed_data)} addresses.")
    return parsed_data


async def parse_address(item: dict, address: str, parsed_data: list):
    try:
        address_dict = parse(address)
    except KeyError as e:
        logging.error(f"Error parsing address: {e}")
        address_dict = {}

    parsed_data.append({**item, **address_dict})


# async def translate_item(item: dict, translated_data: list):
#     data = {}

#     for key, value in item.items():
#         translated_key = japanese_to_english.get(key, key)
#         data[translated_key] = value

#         if translated_key == "Location":
#             address = await parse_address(value)
#             data.update(address)

#     translated_data.append(data)


# async def parse_address(value):
#     address = {}
#     address["prefecture"] = ""
#     address["prefecture_eng"] = ""
#     address["city"] = ""
#     address["city_eng"] = ""
#     address["ward"] = ""
#     address["ward_eng"] = ""
#     address["district"] = ""
#     address["district_eng"] = ""
#     address["town"] = ""
#     address["town_eng"] = ""
#     address["city_district"] = ""
#     address["city_district_eng"] = ""
#     address["unparsed_right"] = ""
#     address["unparsed_left"] = ""

#     try:
#         addresses = parse(value)
#         address.update(addresses)
#     except Exception as e:
#         logging.error(f"Error parsing address: {e}")

#     return address
