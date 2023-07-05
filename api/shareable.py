from bson.objectid import ObjectId
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from loguru import logger


class PlanData(BaseModel):
    json_string: str
    validation_levels: list[int]


class MongoDBConnection:
    def __init__(self):
        self.client = AsyncIOMotorClient("mongodb://localhost:27017")
        self.database = self.client["plans"]
        self.collection = self.database["links"]

    async def get_record(self, id):
        record = await self.collection.find_one({"_id": ObjectId(id)})
        return record

    async def add_record(self, data):
        data = {
            "json_data": data.json_string,
            "validation_levels": data.validation_levels,
        }
        result = await self.collection.insert_one(data)
        return str(result.inserted_id)

    async def check(self):
        try:
            client = AsyncIOMotorClient("mongodb://localhost:27017")
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

    async def close(self):
        self.collection = None
        self.database = None
        self.client.close()


async def get_mongo_conn():
    mongo_conn = MongoDBConnection()
    try:
        yield mongo_conn
    finally:
        await mongo_conn.close()
