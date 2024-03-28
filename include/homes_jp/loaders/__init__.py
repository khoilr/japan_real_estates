from airflow.decorators import task
from include.homes_jp.loaders.mongo import to_mongo
from include.homes_jp.loaders.one_c import one_c


@task
def load_to_mongo(collection: str, data: list):
    to_mongo(collection, data)


@task
def load_to_one_c(data):
    one_c(data)
