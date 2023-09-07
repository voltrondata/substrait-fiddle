import os
from bson.objectid import ObjectId
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient

DEFAULT_MONGO_URL = "mongodb://localhost:27017"


class PlanData(BaseModel):
    json_string: str
    validator_overrides: list[int]


class MongoDBConnection:
    def __init__(self):
        url = os.environ.get("PROD_MONGO_URL", DEFAULT_MONGO_URL)
        self.client = AsyncIOMotorClient(url)

    def initialize(self):
        database = self.client["plans"]
        collection = database["links"]
        return collection

    async def get_record(self, collection, id):
        record = await collection.find_one({"_id": ObjectId(id)})
        return record

    async def add_record(self, collection, data):
        data = {
            "json_string": data.json_string,
            "validator_overrides": data.validator_overrides,
        }
        result = await collection.insert_one(data)
        return str(result.inserted_id)

    async def check(self):
        try:
            url = os.environ.get("PROD_MONGO_URL", "mongodb://localhost:27017")
            client = AsyncIOMotorClient(url)
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
