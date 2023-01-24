from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_ping():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json() == {
        "api_service": "up and running",
    }


def test_parse():
    res = client.post(
        "/init/duckdb/",
        data=["CREATE TABLE test (field1 text, field2 int);"],
    )
    assert res.status_code == 200
    assert res.json() == {{"message": "DuckDB Operation successful"}}
