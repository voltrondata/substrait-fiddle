from fastapi import FastAPI, HTTPException, status, File, UploadFile, Form
from fastapi.openapi.utils import get_openapi
from fastapi_health import health

import substrait_validator as sv

from backend.duckdb import (
    ConnectDuckDB,
    CheckDuckDBConnection,
    ExecuteDuckDb,
    ParseFromDuckDB,
)

from loguru import logger

app = FastAPI()
con = None


@app.get("/")
def ping():
    return {"api_service": "up and running"}


@app.on_event("startup")
def Initialize():
    global con
    con = ConnectDuckDB()


@app.get("/health/duckcb/")
def CheckBackendConn(conn):
    CheckDuckDBConnection(conn)


app.add_api_route("/health", health([CheckBackendConn]))


@app.post("/validate/", status_code=status.HTTP_200_OK)
async def Validate(plan: dict, override_levels: list[int]):
    try:
        logger.info("Validating plan using substrait-validator!")
        config = sv.Config()
        for level in override_levels:
            config.override_diagnostic_level(level, "warning", "info")
        sv.check_plan_valid(plan, config)
        logger.info("Plan validated successfully!")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Substrait Validator Internal Error: " + str(e)
        )


@app.post("/validate/file/", status_code=status.HTTP_200_OK)
async def ValidateFile(file: UploadFile = File(), override_levels: list[int] = Form()):
    try:
        logger.info("Validating file using substrait-validator!")
        config = sv.Config()
        for level in override_levels:
            config.override_diagnostic_level(level, "warning", "info")
        data = await file.read()
        sv.check_plan_valid(data, config)
        logger.info("File validated successfully!")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Substrait Validator Internal Error: " + str(e)
        )


@app.post("/execute/duckdb/", status_code=status.HTTP_200_OK)
async def ExecuteBackend(data: list[str]):
    global con
    return ExecuteDuckDb(data, con)


@app.post("/parse/", status_code=status.HTTP_200_OK)
async def ParseToSubstrait(data: dict):
    global con
    return ParseFromDuckDB(data, con)


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
