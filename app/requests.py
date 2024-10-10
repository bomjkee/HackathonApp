from typing import Dict
from fastapi import FastAPI

app = FastAPI()

@app.get('/')
async def hello_async() -> Dict[str, str]:
    return {"message": "Hello world"}