from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator, ConfigDict


class SHackathon(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="Название")
    description: str = Field(..., min_length=2, description="Описание")
    max_members: int = Field(..., description="Количество участников (должно быть числом)")
    start_date: datetime = Field(..., description="Дата начала")