import trio
from airflow.decorators import task
from real_estates.homes_jp.transformers.parse_address import _transform_parse_address
from real_estates.homes_jp.transformers.translate import _translate
from real_estates.homes_jp.transformers.normalize import _normalize


@task(show_return_value_in_logs=False)
def transform_parse_address(data: list):
    return trio.run(_transform_parse_address, data)


@task(show_return_value_in_logs=False)
def transform_translate(data: list):
    return trio.run(_translate, data)


@task(show_return_value_in_logs=False)
def transform_normalize(data: list):
    return trio.run(_normalize, data)
