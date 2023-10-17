import json

import jwt
import substrait_validator as sv
from duckdb import DuckDBPyConnection
from fastapi import (Depends, FastAPI, File, Form, HTTPException, UploadFile,
                     status)
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordBearer
from fastapi_health import health
import jwt

from motor.motor_asyncio import AsyncIOMotorCollection
import json

from duckdb import DuckDBPyConnection

import substrait_validator as sv

from backend.duckdb import (DuckDBConnection, check_duckdb_connection,
                            delete_table_from_duckDB, execute_duckdb,
                            parse_from_duckDB)
from backend.ttl_cache import TTL_Cache

from loguru import logger

router = APIRouter()

async def get_mongo_conn():
    return app.state.mongo_pool.initialize()


async def get_duck_conn():
    conn = app.state.duck_pool.get_connection()
    try:
        yield conn
    finally:
        conn.close()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=allowed_urls[3])


def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, "key", algorithms=["HS256"])
        return payload
    except jwt.exceptions.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credential validation unsuccessful",
            headers={"WWW-Authenticate": "Bearer"},
        )



@router.on_event("startup")
async def initialize():
    app.state.mongo_pool = MongoDBConnection()
    app.state.duck_pool = DuckDBConnection()
    app.state.schema_cache = TTL_Cache(
        maxsize=100,
        ttl=3600,
        on_expire=lambda key, _: delete_table_from_duckDB(key,
                                                          get_duck_conn()),
    )


@app.get("/health/duckdb/")
def check_backend_conn(conn):
    check_duckdb_connection(conn)
    app.state.mongo_pool.check()


router.add_api_route("/health", health([check_backend_conn]))


@router.post("/validate/", status_code=status.HTTP_200_OK)
async def validate(plan: dict, override_levels: list[int]):
    try:
        logger.info("Validating plan using substrait-validator!")
        config = sv.Config()
        for level in override_levels:
            config.override_diagnostic_level(level, "warning", "info")
        sv.check_plan_valid(plan, config)
        logger.info("Plan validated successfully!")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Substrait Validator Internal Error: "
            + str(e)
        )


@app.post("/validate/file/", status_code=status.HTTP_200_OK)
async def validate_file(file: UploadFile = File(),
                        override_levels: list[int] = Form()):
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
            status_code=500, detail="Substrait Validator Internal Error: "
            + str(e)
        )

@router.post("/save/")
async def SavePlan(
    data: PlanData, db_conn: AsyncIOMotorCollection = Depends(get_mongo_conn)
):
    response = await app.state.mongo_pool.add_record(db_conn, data)
    return response


@router.post("/fetch/")
async def FetchPlan(id: str, db_conn: AsyncIOMotorCollection = Depends(get_mongo_conn)):
    response = await app.state.mongo_pool.get_record(db_conn, id)
    if response is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {
        "json_string": response["json_string"],
        "validator_overrides": response["validator_overrides"],
    }

@router.post("/execute/duckdb/")
def ExecuteBackend(data: dict, db_conn: DuckDBPyConnection = Depends(get_duck_conn)):
    response = ExecuteDuckDb(data, db_conn)
    return response

@router.post("/add_schema/")
def AddSchema(
    data: dict,
    headers: dict = Depends(verify_token),
    db_conn: DuckDBPyConnection = Depends(get_duck_conn),
):
    user_id = headers["user_id"]
    schema = data.get("schema")
    json_data = json.loads(schema["schema"])
    table_name = json_data["table"] + "_" + user_id

    query = "CREATE TABLE IF NOT EXISTS "
    query += table_name + "("
    for field in json_data["fields"]:
        query += field["name"] + " "
        query += field["type"] + " "
        for props in field["properties"]:
            query += props + " "
        query += ", "
    query = query[:-2]
    query += ");"

    response = execute_duckdb(query, db_conn)
    app.state.schema_cache[table_name] = None
    return response


@app.post("/parse/", status_code=status.HTTP_200_OK)
def parse_to_substrait(
    data: dict,
    headers: dict = Depends(verify_token),
    db_conn: DuckDBPyConnection = Depends(get_duck_conn),
):
    response = parse_from_duckDB(data.get("query"), db_conn)
    return response


# For defining custom documentation for the server
def substrait_fiddle_openapi():
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

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["substrait-fiddle.com", "*.substrait-fiddle.com", "127.0.0.1"],
)

@app.get("/")
def global_ping():
    return {"api_service": "up and running"}
