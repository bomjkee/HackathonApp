from pydantic import BaseModel

class Error(BaseModel):
    error: str

class SError(BaseModel):
    status: str
    data: Error