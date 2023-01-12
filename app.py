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
