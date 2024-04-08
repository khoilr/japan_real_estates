from airflow.decorators import task
from real_estates.homes_jp.loaders.mongo import upsert
from real_estates.homes_jp.loaders.one_c import one_c

import asyncio


@task(show_return_value_in_logs=False)
def load_to_mongo(collection: str, filter_keys: list, data: list):
    upsert(collection, filter_keys, data)


@task(show_return_value_in_logs=False)
def load_to_one_c(data):
    asyncio.run(one_c(data))
