from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, ConfigDict, Field, field_validator


class SUser(BaseModel):
    id: int = Field(..., description="ID пользователя")
    telegram_id: int = Field(..., description="Telegram ID пользователя")
    username: str = Field(..., description="Telegram username пользователя")
    first_name: str | None = Field(None, description="Имя tg пользователя")
    last_name: str | None = Field(None, description="Фамилия tg пользователя")

    full_name: str | None = Field(..., description="ФИО пользователя")
    is_student_mirea: bool | None = Field(..., description="Является ли пользователь студентом МИРЭА")
    group: str | None = Field(None, description="Учебная группа пользователя")

    last_active: int | None = Field(None, description="Время последней активности пользователя")


class SUserInfo(BaseModel):
    id: int = Field(..., description="ID пользователя")
    username: str | None = Field(None, description="Tg username пользователя")
    first_name: str | None = Field(None, description="Tg first name пользователя")
    last_name: str | None = Field(None, description="Tg last name пользователя")


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
    start_date: int | None = Field(None, description="Дата начала")
    end_date: int | None = Field(None, description="Дата окончания")


class STeam(BaseModel):
    id: int = Field(..., description="ID команды")
    name: str = Field(..., description="Название команды")
    is_open: bool = Field(..., description="Открыта ли команда для новых участников")
    description: str | None = Field(None, description="Описание команды")
    hackathon_id: int = Field(..., description="ID хакатона")


class ProfileInfo(BaseModel):
    user: SUserInfo = Field(..., description="Информация о пользователе")
    team: STeam | None = Field(None, description="Информация о команде")


class SMember(BaseModel):
    user_id: int = Field(..., description="ID пользователя")
    team_id: int = Field(..., description="ID команды")
    username: str = Field(..., description="Tg username пользователя")
    role: str = Field(..., description="Роль участника")


class STeamWithMembers(BaseModel):
    team: STeam = Field(..., description="Текущая команда")
    members: List[SMember] = Field(..., description="Участники команды")


class SInvite(BaseModel):
    id: int = Field(..., description="ID приглашения")
    invite_user_id: int = Field(..., description="ID приглашаемого пользователя")
    team_id: int = Field(..., description="ID команды")


class Error(BaseModel):
    error: str


class ErrorResponse(BaseModel):
    status: str
    data: Error