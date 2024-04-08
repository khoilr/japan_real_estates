import logging

from airflow.providers.mongo.hooks.mongo import MongoHook
from pymongo import UpdateOne
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import BulkWriteError


def upsert(
    collection: str,
    filter_keys: list,
    data,
):
    mongo_hook = MongoHook(mongo_conn_id="mongo")
    mongo_client = mongo_hook.get_conn()

    db: Database = mongo_client.real_estates
    collection: Collection = db[collection]

    try:
        if isinstance(data, list):
            if isinstance(data[0], dict):
                # Scenario 1: Data is a list of dictionaries
                operations = [
                    UpdateOne(
                        {key: item[key] for key in filter_keys},
                        {"$set": item},
                        upsert=True,
                    )
                    for item in data
                ]
            else:
                # Scenario 2: Data is a list of items
                operations = [
                    UpdateOne(
                        {key: item for key in filter_keys},
                        {"$set": item},
                        upsert=True,
                    )
                    for item in data
                ]
        else:
            raise ValueError("Invalid data format")

        collection.bulk_write(operations)

        logging.info(f"Upserted {len(operations)} documents")
    except BulkWriteError as e:
        logging.error(e.details)

    mongo_client.close()
