from fastapi import FastAPI, HTTPException, status, File, UploadFile, Form, Depends
from fastapi.openapi.utils import get_openapi
from fastapi_health import health

import substrait_validator as sv

from backend.duckdb import (
    ConnectDuckDB,
    CheckDuckDBConnection,
    ExecuteDuckDb,
    ParseFromDuckDB,
)

from shareable import MongoDBConnection, PlanData, get_mongo_conn

from loguru import logger

app = FastAPI()
duckConn = None


@app.get("/")
def ping():
    return {"api_service": "up and running"}


@app.on_event("startup")
async def Initialize():
    global duckConn
    duckConn = ConnectDuckDB()


@app.get("/health/duckdb/")
def CheckBackendConn(conn):
    CheckDuckDBConnection(conn)


@app.get("/health/mongodb/")
def CheckMongoConn(db: MongoDBConnection = Depends(get_mongo_conn)):
    db.check()


app.add_api_route("/health", health([CheckBackendConn]))


@app.post("/validate/")
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


@app.post("/validate/file/")
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


@app.post("/execute/duckdb/")
async def ExecuteBackend(data: list[str]):
    global duckConn
    return ExecuteDuckDb(data, duckConn)


@app.post("/parse/")
async def ParseToSubstrait(data: dict):
    global duckConn
    return ParseFromDuckDB(data, duckConn)


@app.post("/save/")
async def SavePlan(data: PlanData, db: MongoDBConnection = Depends(get_mongo_conn)):
    response = await db.add_record(data)
    return response


@app.post("/fetch/", status_code=status.HTTP_200_OK)
async def FetchPlan(id: str, db: MongoDBConnection = Depends(get_mongo_conn)):
    response = await db.get_record(id)
    return response["json_data"], response["validation_levels"]


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
