from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field, validator, field_validator


class TelegramIDModel(BaseModel):
    telegram_id: int = Field(..., description="Telegram ID")

    model_config = ConfigDict(from_attributes=True)


class IdModel(BaseModel):
    id: int = Field(..., description="ID объекта")


class NameModel(BaseModel):
    name: str = Field(..., description="Имя объекта")


class UserInfoFromBot(TelegramIDModel):
    username: str | None = Field(None, description="Tg username пользователя")
    first_name: str | None = Field(None, description="Tg first name пользователя")
    last_name: str | None = Field(None, description="Tg last name пользователя")


class UserInfoUpdate(BaseModel):
    full_name: str = Field(..., description="ФИО пользователя")
    is_mirea_student: bool = Field(False, description="Является ли пользователь студентом МИРЭА")
    group: str | None = Field(None, description="Учебная группа пользователя")

    @field_validator("full_name")
    def validate_full_name(cls, full_name: str):
        allowed_chars = "ёйцукенгшщзхъфывапролджэячсмитьбюЁЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ - "
        if not all(char in allowed_chars for char in full_name):
            raise ValueError("ФИО должно содержать только русские буквы, пробелы и дефисы")
        return full_name


class TeamCreate(BaseModel):
    name: str  = Field(None, description="Имя команды")
    is_open: bool = Field(..., description="Тип: открытый/закрытый")
    description: str | None = Field(None, description="Описание команды")
    hackathon_id: int = Field(..., description="ID хакатона")


class TeamUpdate(BaseModel):
    name: str | None = Field(None, description="Название команды")
    is_open: bool | None = Field(None, description="Открыта ли команда для новых участников")
    description: str | None = Field(None, description="Описание команды")


class MemberCreate(BaseModel):
    user_id: int = Field(..., description="ID пользователя")
    team_id: int = Field(..., description="ID команды")
    tg_name: str = Field(..., description="Tg username пользователя")
    role: str = Field("member", description="Роль участника")


class MemberLeaderFind(BaseModel):
    user_id: int = Field(..., description="ID пользователя")
    team_id: int = Field(..., description="ID команды")
    role: str = Field("leader", description="Роль участника")


class MemberFind(BaseModel):
    user_id: int | None= Field(None, description="ID пользователя")
    team_id: int = Field(..., description="ID команды")
    hackathon_id: int | None = Field(None, description="ID хакатона")


class InviteFilter(BaseModel):
    invite_user_id: int = Field(..., description="ID приглашаемого пользователя")

class InviteCreate(BaseModel):
    invite_user_id: int = Field(..., description="ID приглашаемого пользователя")
    team_id: int = Field(..., description="ID команды")