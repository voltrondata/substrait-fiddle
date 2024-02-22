from datetime import datetime
import os

from bson.objectid import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from pymongo import ASCENDING

DEFAULT_MONGO_URL = "mongodb://localhost:27017"

############################################################
# Class representing model for substrait plan and override 
# levels to be used for Save/Fetch plans.
############################################################
class PlanData(BaseModel):
    json_string: str
    validator_overrides: list[int]



############################################################
# Class to manage MongoDB connections 
############################################################
class MongoDBConnection:
    def __init__(self):
        url = os.environ.get("PROD_MONGO_URL", DEFAULT_MONGO_URL)
        self.client = AsyncIOMotorClient(url)

    def initialize(self):
        database = self.client["plans"]
        collection = database["links"]

        # TTL index in the createdAt field to expire record after a week
        collection.create_index([("createdAt", ASCENDING)], expireAfterSeconds=604800)

        return collection

    async def get_record(self, collection, id):
        record = await collection.find_one({"_id": ObjectId(id)})
        return record

    async def add_record(self, collection, data):
        data = {
            "json_string": data.json_string,
            "validator_overrides": data.validator_overrides,
            "createdAt": datetime.utcnow()
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
