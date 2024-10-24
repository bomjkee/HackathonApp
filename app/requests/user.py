from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, validator


class RBUser(BaseModel):
    tg_id: int
    username: Optional[str] 
    first_name: Optional[str]
    last_name: Optional[str]


class RBIsStudent(BaseModel):
    id: int
    is_student: bool
    group: Optional[str] = None
    passport: Optional[str] = None
