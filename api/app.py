from fastapi import FastAPI, HTTPException, status, File, UploadFile, Form, Depends, Request
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRouter
from fastapi_health import health

from motor.motor_asyncio import AsyncIOMotorCollection

import substrait_validator as sv

from backend.duckdb import (
    ConnectDuckDB,
    CheckDuckDBConnection,
    ExecuteDuckDb,
    ParseFromDuckDB,
)

from shareable import MongoDBConnection, PlanData

from loguru import logger

router = APIRouter()
duckConn = None

async def get_mongo_conn():
    return app.state.mongo_pool.initialize()

@router.on_event("startup")
def Initialize():
    global duckConn
    duckConn = ConnectDuckDB()
    app.state.mongo_pool = MongoDBConnection()


@router.get("/health/duckcb/")
def CheckBackendConn(conn):
    CheckDuckDBConnection(conn)
    app.state.mongo_pool.check()

router.add_api_route("/health", health([CheckBackendConn]))


@router.post("/validate/")
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


@router.post("/validate/file/")
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


@router.post("/execute/duckdb/")
async def ExecuteBackend(data: list[str]):
    global duckConn
    return ExecuteDuckDb(data, duckConn)


@router.post("/parse/")
async def ParseToSubstrait(data: dict):
    global duckConn
    return ParseFromDuckDB(data, duckConn)


@app.post("/save/")
async def SavePlan(
    data: PlanData, db_conn: AsyncIOMotorCollection = Depends(get_mongo_conn)
):
    response = await app.state.mongo_pool.add_record(db_conn, data)
    return response


@app.post("/fetch/")
async def FetchPlan(id: str, db_conn: AsyncIOMotorCollection = Depends(get_mongo_conn)):
    response = await app.state.mongo_pool.get_record(db_conn, id)
    if response is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {
        "json_string": response["json_string"],
        "validator_overrides": response["validator_overrides"],
    }


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

app = FastAPI()
app.include_router(router, prefix="/api")
app.openapi = SubstraitFiddleOpenAPI

@app.get("/")
def global_ping():
    return {"api_service": "up and running"}
