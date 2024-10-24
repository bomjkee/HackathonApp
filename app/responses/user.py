from typing import Optional, List
from pydantic import BaseModel, Field, validator, ConfigDict

class SStudent(BaseModel):
    id: int
    group: str

    model_config = ConfigDict(from_attributes=True)
        
class SNonStudent(BaseModel):
    id: int
    passport: str

    model_config = ConfigDict(from_attributes=True)

class SUser(BaseModel):
    tg_id: int
    username: Optional[str] 
    first_name: Optional[str] 
    last_name: Optional[str]
    is_student: Optional[SStudent] = None
    is_not_student: Optional[SNonStudent] = None

    model_config = ConfigDict(from_attributes=True)