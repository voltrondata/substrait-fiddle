from pymongo import MongoClient
from uuid import uuid4


class MongoDBConnection:
    def __init__(self):
        self.client = MongoClient("localhost", 27017)
        self.db = self.client["plans"]
        self.collection = self.db["links"]

    def get_record(self, id: str):
        return self.collection.find_one({"id": id})

    def add_record(self, id, json_string, validation_levels):
        data = {
            "id": id,
            "json_data": json_string,
            "validation_levels": validation_levels,
        }
        self.collection.insert_one(data)

    def check():
        try:
            client = MongoClient()
        except Exception as e:
            return False, str(e)

        if "plans" not in client.list_database_names():
            return False, f"Plan database does not exist."

        db = client["mongo"]
        if "links" not in db.list_collection_names():
            return (
                False,
                "Links collection doesn't exist in Plan database.",
            )
