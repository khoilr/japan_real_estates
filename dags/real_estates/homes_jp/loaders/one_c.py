import logging

import aiohttp


async def one_c(data: list):
    async with aiohttp.ClientSession("http://") as session:
        for item in data:
            if item["price"] == 0:
                continue

            payload = {
                "Description": item["name"],
                "Ref": "{}_{}".format(item["url"], item["language"]),
                "Language": item["language"],
                "Address": item["address"],
                # "Logitude": 35.69671110224403,
                # "Latitude": 139.69089329839673,
                "LocationDescription": "; ".join(item["traffics"]),
                "PriceJP": item["max_price"] if "max_price" in item else item["price"],
                # "PriceUSA": 2451150,
                # "BI_PropertyType": item["type"].title(),
                # "BI_Structure": "Reinforced concrete",
                # "BI_OperationYear": "YYYYMMDD"
                "BI_TotalArea": item["max_building_area"] if "max_building_area" in item else item["building_area"],
                # "BI_NumberOfUnits": 10, # Tầng
                # "BI_InspectionCertificate": "None",
                # "BI_LegalRestriction": "Fire Prevention Area",
                # "BI_ParkingPlot": "No",
                # "BI_FirePreventionRegulation": "",
                # "BI_CurrentStatus": "",
                # "BI_Lifeline": "",
                # "BI_Delivery": "",
                # "BI_AltitudeArea": "",
                # "BI_OtherRestriction": "",
                # "LI_Right": "Ownership",
                "LI_Area": item["max_land_area"] if "max_land_area" in item else item["land_area"],
                # "LI_ActualArea": 0,
                # "LI_SiteArea": 0,
                # "LI_BuildingCoverageRatio": 0,
                # "LI_FloorAreaRatio": 0,
                # "LI_VolumnRatio": 0,
                # "LI_FacingRoad": "Northside road width approx. 8m, access road approx. 6.3m",
                # "LI_RoadEquity": "No",
                # "LI_AccessSituation": "",
                # "LI_Type": "Stores, residences, apartments",
                # "LI_UrbanPlanning": "",
                # "BI_AltitudeArea": "",
                "PictureURL": item["images"],
                # "MapURL": "https://www.google.com/maps/place/35.69671110224403,139.69089329839673",
                "City": item["city_eng"] if "city_eng" in item else None,
                "Prefecture": item["prefecture_eng"] if "prefecture_eng" in item else None,
                "Ward": item["ward_eng"] if "ward_eng" in item else None,
                "AddressDetail": item["unparsed_right"] if "unparsed_right" in item else None,
            }

            async with session.post(url="/RealEstate/hs/RealEstate/V1/RealEstate", json=payload) as response:
                logging.info(f"Inserted data to 1C with code {response.status}")
