from airflow.decorators import dag
from pendulum import datetime

from real_estates.homes_jp.extractors import (
    extract_real_estate_urls,
    extract_real_estates,
    extract_v2,
)
from real_estates.homes_jp.loaders import load_to_mongo, load_to_one_c
from real_estates.homes_jp.transformers import (
    transform_normalize,
    transform_parse_address,
    transform_translate,
)


@dag(schedule_interval="@daily", start_date=datetime(2024, 1, 1), catchup=False)
def real_estates():
    urls = extract_real_estate_urls()
    load_to_mongo("urls", ["url"], urls)

    real_estates = extract_real_estates(urls)
    load_to_mongo("raw", ["url"], real_estates)

    normalized_real_estates = transform_normalize(real_estates)
    parsed_address_real_estates = transform_parse_address(normalized_real_estates)

    load_to_mongo("normalized", ["url"], parsed_address_real_estates)

    load_to_one_c(parsed_address_real_estates)

    # data_v2 = extract_v2()

    # translated_data = transform_translate(parsed_address_real_estates)
    # load_to_mongo("translated", ["url"], translated_data)


real_estates()
