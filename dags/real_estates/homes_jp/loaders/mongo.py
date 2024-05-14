import logging
from datetime import datetime
from typing import Dict, List

from airflow.providers.mongo.hooks.mongo import MongoHook
from pymongo import UpdateOne
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import BulkWriteError


def upsert(
    collection: str,
    filter_keys: list,
    data: List[Dict],
):
    """
    Upserts the given data into the specified collection in MongoDB.

    Args:
        collection (str): The name of the collection to upsert the data into.
        filter_keys (list): The list of keys to use as filters for upserting the data.
        data (List[Dict]): The list of dictionaries containing the data to upsert.

    Returns:
        None
    """
    # Establish a connection to MongoDB
    mongo_hook = MongoHook(mongo_conn_id="mongo")
    mongo_client = mongo_hook.get_conn()

    # Get the database and collection
    db: Database = mongo_client.real_estates
    collection: Collection = db[collection]

    try:
        # Prepare the bulk write operations
        operations = [
            UpdateOne(
                filter={key: item[key] for key in filter_keys},
                update={
                    "$set": {**item, "updated_at": datetime.now()},
                    "$setOnInsert": {"created_at": datetime.now()},
                },
                upsert=True,
            )
            for item in data
        ]

        # Execute the bulk write operations
        collection.bulk_write(operations)

        # Log the number of documents upserted
        logging.info(f"Upserted {len(operations)} documents")

    except BulkWriteError as e:
        logging.error(e.details)

    # Close the MongoDB connection
    mongo_client.close()
