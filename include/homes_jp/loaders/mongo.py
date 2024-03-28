from airflow.providers.mongo.hooks.mongo import MongoHook


def to_mongo(collection: str, data: list):
    mongo_hook = MongoHook(mongo_conn_id="mongo")
    mongo_client = mongo_hook.get_conn()

    db = mongo_client.db
    db[collection].insert_many(data)
