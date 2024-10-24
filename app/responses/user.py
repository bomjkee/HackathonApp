from typing import Optional, List
from pydantic import BaseModel, Field, validator, ConfigDict



class SUser(BaseModel):
    tg_id: int = Field(..., description="ID пользователя")
    username: Optional[str] = Field(None, description="username пользователя")
    full_name: Optional[str] = Field(None, description="Tg full name name пользователя")

    photo_url: Optional[str] = Field(None, description="URL фото пользователя")
    auth_date: Optional[str] = Field(None, description="Дата авторизации")
    hash: Optional[str] = Field(None, description="Хэш")

    fio: Optional[str] = Field(None, description="ФИО пользователя")
    is_mirea_student: Optional[bool] = Field(None, description="Студент ли МИРЭА")
    passport: Optional[str] = Field(None, description="Паспортные данные")
