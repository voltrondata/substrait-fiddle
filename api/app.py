import json

import substrait_validator as sv
from duckdb import DuckDBPyConnection
from fastapi import (Depends, FastAPI, File, Form, HTTPException, UploadFile,
                     status)
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRouter
from fastapi_health import health
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorCollection

from components.auth import verify_token
from components.duckdb import (DuckDBConnection, check_duckdb_connection,
                               delete_table_from_duckDB, execute_duckdb,
                               parse_from_duckDB)
from components.shareable import MongoDBConnection, PlanData
from components.ttl_cache import TTL_Cache

router = APIRouter()


############################################################
# Functions to request db objects from connection pools
############################################################
async def get_mongo_conn():
    return app.state.mongo_pool.initialize()

async def get_duck_conn():
    conn = app.state.duck_pool.get_connection()
    try:
        yield conn
    finally:
        conn.close()



############################################################
# Initialization function to be called during startup
############################################################
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



############################################################
# API Endpoint to check health of backend components
############################################################
def check_backend_conn(conn):
    check_duckdb_connection(conn)
    app.state.mongo_pool.check()

router.add_api_route("/health", health([check_backend_conn]))



############################################################
# API Endpoint to validate a substrait plan
############################################################
@router.post("/validate/", status_code=status.HTTP_200_OK)
async def validate(plan: dict, override_levels: list[int]):
    '''
    Validates a plan using the substrait-validator 
    with overriding rules as specified and returns 
    errors accordingly.

    Parameters:
        plan (dict): Substrait JSON plan
        override_levels (list[int]): List of validation
                                        override levels
    
    Returns:
        Success message upon validation otherwise Exception
        with failure message.
    '''
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
    


############################################################
# API Endpoint to validate file containing a substrait plan
############################################################
@router.post("/validate/file/", status_code=status.HTTP_200_OK)
async def validate_file(file: UploadFile = File(),
                        override_levels: list = Form()):
    '''
    Validates a file using the substrait-validator 
    with overriding rules as specified and returns 
    errors accordingly.

    Parameters:
        file (File): File object to read and validate
        override_levels (list[int]): List of validation
                                        override levels
    
    Returns:
        Success message upon validation otherwise Exception
        with failure message.
    '''
    try:
        logger.info("Validating file using substrait-validator!")
        override_levels = [int(level) for level in override_levels[0].split(',')]
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



############################################################
# API Endpoint to save a substrait plan
############################################################
@router.post("/save/")
async def save_plan(
    data: PlanData, db_conn: AsyncIOMotorCollection = Depends(get_mongo_conn)
):
    '''
    Saves a Substrait plan to MongoDB and returns a unique ID 
    that can be used to fetch it later.

    Parameters:
        data (PlanData): Substrait Plan
        db_conn: MongoDB connection object

    Returns:
        Unique ID of the inserted plan
    '''
    response = await app.state.mongo_pool.add_record(db_conn, data)
    return response



############################################################
# API Endpoint to fetch a saved substrait plan
############################################################
@router.post("/fetch/")
async def fetch_plan(id: str, 
                     db_conn: AsyncIOMotorCollection = Depends(get_mongo_conn)):
    '''
    Fetches a saved Substrait plan from MongoDB

    Parameters:
        id (str): Plan ID 
        db_conn: MongoDB connection object
    
    Returns:
        Substrait JSON plans if present otherwise
        HTTPException is raised
    '''
    response = await app.state.mongo_pool.get_record(db_conn, id)
    if response is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {
        "json_string": response["json_string"],
        "validator_overrides": response["validator_overrides"],
    }



############################################################
# API Endpoint to add schema in DuckDB instance
############################################################
@router.post("/add_schema/")
def add_schema(
    data: dict,
    headers: dict = Depends(verify_token),
    db_conn: DuckDBPyConnection = Depends(get_duck_conn),
):
    '''
    Creates a table in DuckDB to allow SQL queries
    on them for further parsing. API requires 
    authentication to internally store tables
    with specified user_id. API accepts the schema
    in a format specified in the front-end and 
    builds the SQL CREATE statement before executing it.

    Parameters:
        data (dict): API request containing the schema
        headers (dict): API headers for authentication
        db_conn: DuckDB connection object
    
    Returns:
        Success/Error response
    '''
    user_id = headers["user_id"]
    schema = data["schema"]
    json_data = json.loads(schema)
    table_name = json_data["table"] + "_" + user_id

    query = "CREATE TABLE  "
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



############################################################
# API Endpoint to parse SQL queries to Substrait JSON plans
############################################################
@router.post("/parse/", status_code=status.HTTP_200_OK)
def parse_to_substrait(
    data: dict,
    headers: dict = Depends(verify_token),
    db_conn: DuckDBPyConnection = Depends(get_duck_conn),
):
    '''
    Parses a SQL query to Substrait JSON plans via 
    DuckDB. 

    Parameters:
        data (dict): API request containing the
                        SQL query
        db_conn: DuckDB connection object 
    
    Returns:
        response (dict): Response JSON for translated
                            Substrait plan
    '''
    response = parse_from_duckDB(data.get("query"), db_conn)
    return response



############################################################
# API Declaration
############################################################
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
app.include_router(router, prefix="/api/route")
app.openapi = substrait_fiddle_openapi
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["substrait-fiddle.com", "*.substrait-fiddle.com", "127.0.0.1"],
)

@app.get("/")
def global_ping():
    return {"api_service": "up and running"}
