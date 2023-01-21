from fastapi import FastAPI, HTTPException, status
from fastapi.openapi.utils import get_openapi

from substrait_validator import check_plan_valid
import duckdb

app = FastAPI()
con = None


@app.get("/")
def ping():
    return {"api_service": "up and running"}


@app.on_event("startup")
def Initialize():
    global con
    con = duckdb.connect()
    con.install_extension("substrait")
    con.load_extension("substrait")
    print("DuckDb initialized successfully")


@app.post("/validate/")
async def Validate(data: dict):
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
async def ParseToSubstrait(data: str):
    try:
        global con
        result = con.get_substrait_json(data).fetchone()[0]
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
