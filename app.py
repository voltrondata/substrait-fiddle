import os.path
from urllib import request

from fastapi import FastAPI, HTTPException, status, File
from fastapi.openapi.utils import get_openapi
from fastapi_health import health

from substrait_validator import check_plan_valid
import duckdb

app = FastAPI()
con = None

@app.get("/")
def ping():
    return {"api_service": "up and running"}


def FetchTpchData():
    if not os.path.isfile("lineitemsf1.snappy.parquet"):
        print("File not found, downloading!")
        url = "https://github.com/duckdb/duckdb-data/releases/download/v1.0/lineitemsf1.snappy.parquet"
        response = request.urlretrieve(url, "lineitemsf1.snappy.parquet")
        print("File downloaded successfully!")


def ConnectDB():
    global con
    con = duckdb.connect()
    con.install_extension("substrait")
    con.load_extension("substrait")
    con.install_extension("tpch")
    con.load_extension("tpch")
    con.execute(
        query="CREATE TABLE IF NOT EXISTS lineitem AS SELECT * FROM 'lineitemsf1.snappy.parquet';"
    )
    print("DuckDb initialized successfully")


@app.on_event("startup")
def Initialize():
    FetchTpchData()
    ConnectDB()


@app.get("/health/duckcb/")
def CheckDuckDBConnection(conn):
    status = {"db_health": "unavailable"}
    try:
        conn.execute(query="SHOW TABLES;").fetchall()
        status["db_health"] = "up and running"
    except Exception as e:
        print(
            "Heatlcheck failed for DuckDB, initialize new connection object. Details: ",
            str(e),
        )
    finally:
        return status


app.add_api_route("/health", health([CheckDuckDBConnection]))


@app.post("/validate/")
async def Validate(data: dict):
    try:
        result = await check_plan_valid(data)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Substrait Validator Internal Error: " + str(e)
        )

@app.post("/validate/file/")
async def ValidateFile(data: bytes = File()):
    try:
        result = await check_plan_valid(data)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Substrait Validator Internal Error: " + str(e)
        )


@app.post("/init/duckdb/", status_code=status.HTTP_200_OK)
async def InjectDuckDb(data: list[str]):
    try:
        global con
        for i in data:
            con.execute(query=i)
        return {"message": "DuckDB Operation successful"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Substrait DuckDB Internal Error while parsing SQL Query: " + str(e),
        )


@app.post("/parse/")
async def ParseToSubstrait(data: dict):
    try:
        global con
        if CheckDuckDBConnection(con)["db_health"] != "up and running":
            FetchTpchData()
            ConnectDB()
        print(data)
        result = con.get_substrait_json(data['query']).fetchone()[0]
        print(result)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Substrait DuckDB Internal Error while parsing SQL Query: " + str(e),
        )


# For defining custom documentation for the server
def SubstraitFiddleOpenAPI():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Substrait Fiddle",
        version="0.0.1",
        description="Documentation for Substrait Fiddle APIs",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = SubstraitFiddleOpenAPI
