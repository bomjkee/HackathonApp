from datetime import datetime
from typing import List, TypeVar
from pydantic import BaseModel, Field

from app.api.typization.schemas import TelegramIDModel

T = TypeVar(name="T", bound=BaseModel)

class SUser(BaseModel):
    id: int = Field(..., description="ID пользователя")
    telegram_id: int = Field(..., description="Telegram ID пользователя")
    username: str = Field(..., description="Telegram username пользователя")
    first_name: str | None = Field(None, description="Имя tg пользователя")
    last_name: str | None = Field(None, description="Фамилия tg пользователя")

    full_name: str | None = Field(None, description="ФИО пользователя")
    is_mirea_student: bool | None = Field(None, description="Является ли пользователь студентом МИРЭА")
    group: str | None = Field(None, description="Учебная группа пользователя")



class SUserInfo(TelegramIDModel):
    username: str | None = Field(None, description="Tg username пользователя")
    first_name: str | None = Field(None, description="Tg first name пользователя")
    last_name: str | None = Field(None, description="Tg last name пользователя")



class SUserCheckRegistration(BaseModel):
    is_registered: bool = Field(..., description="Зарегистрирован ли пользователь в MiniApp")


class SUserIsLeader(BaseModel):
    is_leader: bool = Field(False, description="Является ли пользователь лидером команды")


class SHackathons(BaseModel):
    id: int = Field(..., description="ID хакатона")
    name: str = Field(..., description="Название хакатона")
    start_description: str = Field(..., description="Вступительное описание")



class SHackathonInfo(BaseModel):
    id: int = Field(..., description="ID хакатона")
    name: str = Field(..., description="Название хакатона")
    start_description: str = Field(..., description="Вступительное описание")
    description: str = Field(..., description="Описание хакатона")
    max_members: int = Field(..., description="Максимальное количество участников")
    start_date: datetime | None = Field(None, description="Дата начала")
    end_date: datetime | None = Field(None, description="Дата окончания")



class STeam(BaseModel):
    id: int = Field(..., description="ID команды")
    name: str = Field(..., description="Название команды")
    is_open: bool = Field(..., description="Открыта ли команда для новых участников")
    description: str | None = Field(None, description="Описание команды")
    hackathon_id: int = Field(..., description="ID хакатона")



class ProfileInfo(BaseModel):
    user: SUserInfo = Field(..., description="Информация о пользователе")
    teams: List[STeam] | None = Field(..., description="Информация о командах")



class SMember(BaseModel):
    id: int = Field(..., description="ID участника")
    user_id: int = Field(..., description="ID пользователя")
    team_id: int = Field(..., description="ID команды")
    tg_name: str = Field(..., description="Tg username пользователя")
    role: str = Field(..., description="Роль участника")



class STeamWithMembers(BaseModel):
    team: STeam = Field(..., description="Текущая команда")
    members: List[SMember] = Field(..., description="Участники команды")



class SInvite(BaseModel):
    id: int = Field(..., description="ID приглашения")
    invite_user_id: int = Field(..., description="ID приглашаемого пользователя")
    team_id: int = Field(..., description="ID команды")



class SuccessResponse(BaseModel):
    status: str = Field("success", description="Статус ответа")
    message: str = Field(..., description="Сообщение")



class Error(BaseModel):
    code: int = Field(..., description="Код ошибки")
    message: str = Field(..., description="Сообщение об ошибке")


class ErrorResponse(BaseModel):
    status: str = Field(..., description="Статус ответа")
    data: Error = Field(..., description="Данные об ошибке")
