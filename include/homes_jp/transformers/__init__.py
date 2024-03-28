from airflow.decorators import task
from include.homes_jp.transformers.english_keys import english_keys


@task
def transform_to_english_keys(data: list):
    return english_keys(data)
