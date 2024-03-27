from airflow.decorators import task

from include.homes_jp.extractors.regions_and_prefectures import regions_and_prefectures
from include.homes_jp.extractors.real_estates import real_estates


@task
def extract_regions_and_prefectures():
    return regions_and_prefectures()


@task
def extract_real_estates(japan_data: list):
    return real_estates(japan_data)
