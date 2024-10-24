from typing import Optional, List
from pydantic import BaseModel, Field, validator, ConfigDict




class SMember(BaseModel):
    user_id: int = Field(..., description="ID пользователя")
    username: str = Field(..., description="Никнейм пользователя")
    role: Optional[str] = Field(None, description="Роль участника")


class STeam(BaseModel):
    id: int = Field(..., description="ID команды")
    name: Optional[str] = Field(None, description="Имя команды")
    is_open: Optional[bool] = Field(None, description="Открыта ли команда")
    members: List[SMember] = Field([], description="Список участников команды")

