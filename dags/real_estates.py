from airflow.decorators import dag
from pendulum import datetime

from include.homes_jp.extractors import (
    extract_real_estate_urls,
    extract_real_estates,
    extract_regions_and_prefectures,
)
from include.homes_jp.loaders import load_to_mongo, load_to_one_c
from include.homes_jp.transformers import transform_to_english_keys


@dag(
    # schedule_interval="@daily",
    schedule=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
)
def real_estates():
    # Extract the regions and prefectures data from Japan
    japan_data = extract_regions_and_prefectures()

    urls = extract_real_estate_urls(japan_data)

    load_to_mongo("urls", urls)
    real_estates = extract_real_estates(urls)

    load_to_mongo("japanese", real_estates)
    real_estates_english_keys = transform_to_english_keys(real_estates)

    load_to_mongo("english_keys", real_estates_english_keys)
    load_to_one_c(real_estates_english_keys)


real_estates()
