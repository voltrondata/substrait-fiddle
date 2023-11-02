import json
from uuid import uuid4

import jwt
import requests
from fastapi.testclient import TestClient

from app import app


def test_ping():
    with TestClient(app) as client:
        res = client.get("/", headers={"Host": "127.0.0.1"})
        assert res.status_code == 200
        assert res.json() == {
            "api_service": "up and running",
        }


def test_validate_json():
    with TestClient(app) as client:
        url = "https://substrait.io/tutorial/final_plan.json"
        response = requests.get(url)
        assert response.status_code == 200
        plan = response.json()

        data = {
            "plan": plan,
            "override_levels": [2001, 1],
        }
        response = client.post("/route/validate/", json=data, 
                               headers={"Host": "127.0.0.1"})
        assert response.status_code == 200


def test_validate_binary():
    with TestClient(app) as client:
        with open("../resources/plan.bin", 'rb') as file_stream:
            file = file_stream.read()

        response = client.post(
            "/route/validate/file/",
            data={"override_levels": [1002, 2001]},
            files={"file": ("q1.bin", file, "application/octet-stream")},
            headers={"Host": "127.0.0.1"}
        )
        assert response.status_code == 200


def test_add_schema():
    with TestClient(app) as client:
        payload = {"user_id": str(uuid4()).replace('-', '_')}
        token = jwt.encode(payload, "key", algorithm="HS256")
        schema = '''
                {
                "table": "test",
                "fields": [
                    {
                    "name": "field_1",
                    "type": "INTEGER",
                    "properties": [
                        "NOT NULL"
                    ]
                    }
                ]
                }
        '''
        response = client.post(
            "/route/add_schema/",
            json={
                "schema": schema
            },
            headers={"Host": "127.0.0.1",
                     "Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json() is not None


def test_parse_to_substrait():
    with TestClient(app) as client:
        payload = {"user_id": str(uuid4())}
        token = jwt.encode(payload, "key", algorithm="HS256")

        response = client.post(
            "/route/parse/",
            json={
                "query": "SELECT * FROM lineitem;",
            },
            headers={"Host": "127.0.0.1",
                     "Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json() is not None


def test_save_plan_roundtrip():
    with TestClient(app) as client:
        url = "https://substrait.io/tutorial/final_plan.json"
        response = requests.get(url)
        assert response.status_code == 200
        plan = response.json()
        json_string = json.dumps(plan)

        data = {
            "json_string": json_string,
            "validator_overrides": [2001, 1],
        }
        response = client.post("/route/save/", json=data, headers={"Host": "127.0.0.1"})
        assert response.status_code == 200

        response = client.post("/route/fetch/?id=" + response.json(), 
                               headers={"Host": "127.0.0.1"})
        assert response.status_code == 200
        assert response.json()["json_string"] == json_string
        assert response.json()["validator_overrides"] == [2001, 1]
