from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()

@app.get("/")
def ping():
    return {"api_service": "up and running"}
