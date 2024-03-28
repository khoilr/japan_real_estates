import logging
import re

import requests


def one_c(data):
    url = "http://103.157.218.115/RealEstate/hs/RealEstate/V1/RealEstate"

    for item in data:
        # Extract the upper number from the 'Sales Price' field
        sales_price = item["Sales Price"]
        sales_price = re.sub(r"\([^)]*\)", "", sales_price)
        sales_price = sales_price.replace(",", "")
        sale_price_upper = re.findall(r"\d+\.?\d*", sales_price)
        if sale_price_upper:
            sale_price_upper = sale_price_upper[-1]
        else:
            sale_price_upper = 0

        area = item["Exclusive Area"]
        area = re.sub(r"\([^)]*\)", "", area)
        area = area.replace(",", "")
        area_upper = re.findall(r"\d+\.?\d*", area)
        if area_upper:
            area_upper = area_upper[-1]
        else:
            area_upper = 0

        payload = {
            "Description": item["description"],
            "Ref": item["url"],
            "Language": "JP",
            "Address": item["Location"],
            # "Logitude": 35.69671110224403,
            # "Latitude": 139.69089329839673,
            "LocationDescription": item["Access"],
            "PriceJP": float(sale_price_upper),
            # "PriceUSA": 2451150,
            "BI_PropertyType": item["classification"],  # Apartment or house
            # "BI_Structure": "Reinforced concrete",
            # "BI_OperationYear": "YYYYMMDD"
            # "BI_TotalArea": 477,
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
            "LI_Area": float(area_upper),
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
            "PictureURL": item["image_url"],
            # "MapURL": "https://www.google.com/maps/place/35.69671110224403,139.69089329839673",
        }
        response = requests.post(url, json=payload)

        logging.info(f"Inserted data to 1C with code {response.status_code}")
