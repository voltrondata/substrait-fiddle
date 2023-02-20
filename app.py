import os.path
from urllib import request

from fastapi import FastAPI, HTTPException, status, File, UploadFile, Form
from fastapi.openapi.utils import get_openapi
from fastapi_health import health
from pydantic import BaseModel

import substrait_validator as sv
import duckdb

from loguru import logger

app = FastAPI()
con = None


class ValidatePlanModel(BaseModel):
    plan: dict
    override_levels: list[int]


@app.get("/")
def ping():
    return {"api_service": "up and running"}


def FetchTpchData():
    if not os.path.isfile("lineitemsf1.snappy.parquet"):
        logger.info("File not found, downloading!")
        url = (
            "https://github.com/duckdb/duckdb-data/releases/download"
            "/v1.0/lineitemsf1.snappy.parquet"
        )
        request.urlretrieve(url, "lineitemsf1.snappy.parquet")
        logger.success("File downloaded successfully!")


def ConnectDB():
    global con
    con = duckdb.connect()
    con.install_extension("substrait")
    con.load_extension("substrait")
    con.install_extension("tpch")
    con.load_extension("tpch")
    con.execute(
        query="CREATE TABLE IF NOT EXISTS lineitem"
        " AS SELECT * FROM 'lineitemsf1.snappy.parquet';"
    )
    logger.success("DuckDb initialized successfully")


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
        logger.info(
            "Healthcheck failed for DuckDB"
            "Initializing new connection object. Details: ",
            str(e),
        )
    finally:
        return status


app.add_api_route("/health", health([CheckDuckDBConnection]))


@app.post("/validate/", status_code=status.HTTP_200_OK)
async def Validate(data: ValidatePlanModel):
    try:
        config = sv.Config()
        for level in data.override_levels:
            config.override_diagnostic_level(level, "warning", "info")
        sv.check_plan_valid(data.plan, config)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Substrait Validator Internal Error: " + str(e)
        )


@app.post("/validate/file/", status_code=status.HTTP_200_OK)
async def ValidateFile(
    file: UploadFile = File(...), override_levels: list[int] = Form(...)
):
    try:
        config = sv.Config()
        for level in override_levels:
            config.override_diagnostic_level(level, "warning", "info")
        data = await file.read()
        sv.check_plan_valid(data, config)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Substrait Validator Internal Error: " + str(e)
        )


@app.post("/init/duckdb/", status_code=status.HTTP_200_OK)
async def ExecuteDuckDb(data: list[str]):
    try:
        global con
        if CheckDuckDBConnection(con)["db_health"] != "up and running":
            FetchTpchData()
            ConnectDB()
        for i in data:
            con.execute(query=i)
        return {"message": "DuckDB Operation successful"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Substrait DuckDB Internal Error while parsing SQL Query: " + str(e),
        )


@app.post("/parse/", status_code=status.HTTP_200_OK)
async def ParseToSubstrait(data: dict):
    try:
        global con
        if CheckDuckDBConnection(con)["db_health"] != "up and running":
            FetchTpchData()
            ConnectDB()
        result = con.get_substrait_json(data["query"]).fetchone()[0]
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
