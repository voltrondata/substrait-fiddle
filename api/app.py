from fastapi import Depends, FastAPI, HTTPException, status, File, UploadFile, Form
from fastapi.openapi.utils import get_openapi
from fastapi_health import health

import substrait_validator as sv

from backend.duckdb import (
    ConnectDuckDB,
    CheckDuckDBConnection,
    ExecuteDuckDb,
    ParseFromDuckDB,
)

from shareable import MongoDBConnection

from loguru import logger

app = FastAPI()
duckCon = None
mongoColl = MongoDBConnection()


@app.get("/")
def ping():
    return {"api_service": "up and running"}


@app.on_event("startup")
def Initialize():
    global duckCon, mongoColl
    duckCon = ConnectDuckDB()
    mongoColl = ConnectMongo()


@app.get("/health/duckcb/")
def CheckBackendConn(conn):
    CheckDuckDBConnection(conn)


@app.get("/health/mongodb/")
def CheckMongoConn():
    CheckMongoConnection()


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
    global duckCon
    return ExecuteDuckDb(data, duckCon)


@app.post("/parse/", status_code=status.HTTP_200_OK)
async def ParseToSubstrait(data: dict):
    global duckCon
    return ParseFromDuckDB(data, duckCon)


@app.post("/save/", status_code=status.HTTP_200_OK)
async def SavePlan(data: dict, connection: MongoDBConnection = Depends()):
    return connection.add_record(data["json_string"], data["validation_levels"])


@app.post("/fetchplan/", status_code=status.HTTP_200_OK)
async def FetchPlan(uuid: str, connection: MongoDBConnection = Depends()):
    return connection.get_record(uuid)


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
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = SubstraitFiddleOpenAPI
