from bson.objectid import ObjectId

from pydantic import BaseModel
from pymongo import MongoClient

from loguru import logger


class PlanData(BaseModel):
    json_string: str
    validation_levels: list[int]


class MongoDBConnection:
    def __init__(self):
        self.connection = None

    async def connect(self):
        client = MongoClient("localhost", 27017)
        db = client["plans"]

        if "links" not in db.list_collection_names():
            db.create_collection("links")
            logger.info("Created 'links' collection")

        self.collection = db["links"]
        logger.success("MongoDB connection established successfully")

    async def get_record(self, id):
        record = self.collection.find_one({"_id": ObjectId(id)})
        return record

    async def add_record(self, data):
        data = {
            "json_data": data.json_string,
            "validation_levels": data.validation_levels,
        }
        result = self.collection.insert_one(data)
        return str(result.inserted_id)

    def check(self):
        try:
            client = MongoClient("localhost", 27017)
        except Exception as e:
            return False, str(e)

        if "plans" not in client.list_database_names():
            return (False, "Plan database does not exist.")

        db = client["mongo"]
        if "links" not in db.list_collection_names():
            return (
                False,
                "Links collection doesn't exist in Plan database.",
            )
