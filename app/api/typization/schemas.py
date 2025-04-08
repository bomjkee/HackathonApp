from pydantic import BaseModel, ConfigDict, Field, validator, field_validator
from datetime import datetime


class IdModel(BaseModel):
    id: int = Field(..., description="ID объекта")


class NameModel(BaseModel):
    name: str = Field(..., description="Имя объекта")


class HackathonIDModel(BaseModel):
    hackathon_id: int = Field(..., description="ID хакатона")


class TelegramIDModel(BaseModel):
    telegram_id: int = Field(..., description="Telegram ID")

    model_config = ConfigDict(from_attributes=True)


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


class MemberFind(BaseModel):
    id: int | None = Field(None, description="Id приглашения")
    user_id: int | None = Field(None, description="ID пользователя")
    team_id: int | None = Field(None, description="ID команды")
    tg_name: str | None = Field(None, description="Tg username пользователя")
    role: str | None = Field(None, description="Роль участника")


class InviteFilter(BaseModel):
    invite_user_id: int = Field(..., description="ID приглашаемого пользователя")


class InviteCreate(BaseModel):
    invite_user_id: int = Field(..., description="ID приглашаемого пользователя")
    team_id: int = Field(..., description="ID команды")


class HackathonCreate(BaseModel):
    name: str = Field(..., description="Название хакатона")
    start_description: str = Field(..., description="Вступительное описание")
    description: str = Field(..., description="Описание хакатона")
    max_members: int = Field(..., description="Максимальное количество участников")
    start_date: datetime | None = Field(None, description="Дата начала в timestamp")
    end_date: datetime | None = Field(None, description="Дата окончания в timestamp")

    @field_validator("max_members")
    def validate_max_members(cls, v):
        if v < 1:
            raise ValueError("Максимальное количество участников должно быть больше 0")
        return v
