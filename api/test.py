from fastapi.testclient import TestClient
from io import BytesIO
import json
import requests
from app import app

client = TestClient(app)


def test_ping():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json() == {
        "api_service": "up and running",
    }


def test_validate_json():
    url = "https://substrait.io/tutorial/final_plan.json"
    response = requests.get(url)
    assert response.status_code == 200
    plan = response.json()

    data = {
        "plan": plan,
        "override_levels": [2001, 1],
    }
    response = client.post("/validate/", json=data)
    assert response.status_code == 200


def test_validate_binary():
    url = "https://github.com/westonpace/substrait-viewer/blob/main/demo/q1.bin"
    response = requests.get(url)
    file_content = response.content

    file = BytesIO(file_content)

    response = client.post(
        "/validate/file/",
        data={"override_levels": [1002, 1001]},
        files={"file": ("q1.bin", file, "application/octet-stream")},
    )
    assert response.status_code == 200


def test_duckdb_execute():
    res = client.post(
        "/execute/duckdb/",
        json=["CREATE TABLE weather (city VARCHAR, temp_lo INTEGER);"],
    )
    assert res.status_code == 200
    assert res.json() == {"message": "DuckDB Operation successful"}


def test_parse_to_substrait():
    response = client.post("/parse/", json={"query": "SELECT * FROM lineitem;"})
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
        response = client.post("/save/", json=data)
        assert response.status_code == 200

        response = client.post("/fetch/?id=" + response.json())
        assert response.status_code == 200
        assert response.json()["json_string"] == json_string
        assert response.json()["validator_overrides"] == [2001, 1]
