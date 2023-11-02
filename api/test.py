import json
from io import BytesIO

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
        url = (
            "https://github.com/westonpace/"
            "substrait-viewer/blob/main/demo/q1.bin"
        )
        response = requests.get(url)

        file_content = response.content

        file = BytesIO(file_content)

        response = client.post(
            "/route/validate/file/",
            data={"override_levels": [1002, 1001]},
            files={"file": ("q1.bin", file, "application/octet-stream")},
            headers={"Host": "127.0.0.1"}
        )
        assert response.status_code == 200



def test_parse_to_substrait():
    with TestClient(app) as client:
        response = client.post(
            "/route/parse/",
            json={
                "query": "SELECT * FROM lineitem;",
            },
            headers={"Host": "127.0.0.1"}
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
