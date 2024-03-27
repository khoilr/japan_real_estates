from airflow.decorators import dag
from pendulum import datetime

from include.homes_jp.extractors import extract_regions_and_prefectures, extract_real_estates


@dag(
    # schedule_interval="@daily",
    schedule=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
)
def real_estates():
    # Extract the regions and prefectures data from Japan
    japan_data = extract_regions_and_prefectures()

    # Extract real estates data
    extract_real_estates(japan_data)


real_estates()
