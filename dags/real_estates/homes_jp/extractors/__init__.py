import asyncio

from airflow.decorators import task

from real_estates.homes_jp.extractors.real_estates import _extract_real_estates
from real_estates.homes_jp.extractors.regions_and_prefectures import regions_and_prefectures
from real_estates.homes_jp.extractors.urls import _extract_real_estate_urls


@task(show_return_value_in_logs=False)
def extract_regions_and_prefectures():
    return regions_and_prefectures()


@task(show_return_value_in_logs=False)
def extract_real_estates(urls: list):
    return asyncio.run(_extract_real_estates(urls))


@task(show_return_value_in_logs=False)
def extract_real_estate_urls():
    return asyncio.run(_extract_real_estate_urls())
