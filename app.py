from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from substrait_validator import check_plan_valid

app = FastAPI()

@app.get("/")
def ping():
    return {"api_service": "up and running"}

@app.post("/validate/")
async def validate(data: str):
    result = await check_plan_valid(data)
    return result

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
    print(openapi_schema)
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = SubstraitFiddleOpenAPI
