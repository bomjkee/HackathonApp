from typing import Any, Tuple, Dict, Union
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.requests import Request
from fastapi.responses import Response, RedirectResponse

from app.api.typization.exceptions import HackathonNotFoundException, UserNotFoundException
from app.db.dao import UserDAO, TeamDAO, HackathonDAO
from app.api.utils.api_utils import exception_handler
from app.api.utils.auth_dep import fast_auth_user, get_authenticated_user

from app.api.typization.schemas import TelegramIDModel, UserInfoUpdate, IdModel
from app.api.typization.responses import SUser, ErrorResponse, SUserInfo, STeam, ProfileInfo, SUserCheckRegistration
from app.db.session_maker import db
from app.api.utils.redis_operations import make_user_active
from config import redis

router = APIRouter()


@router.post("/register", response_model=Union[dict, ErrorResponse],
             responses={400: {"model": ErrorResponse}})
@exception_handler
async def register_user(user_info: UserInfoUpdate,
                        session: AsyncSession = Depends(db.get_db_with_commit),
                        user: SUser = Depends(fast_auth_user)) -> dict:
    """Регистрирует пользователя (обновляет запись в бд и дописывает фио и группу опционально)"""
    try:
        user = await UserDAO.update(session=session, filters=IdModel(id=user.id), values=user_info)
        if not user:
            raise UserNotFoundException

        user_key = f"user_info:{user.id}"
        await redis.hset(user_key, mapping={
            **user,
            "full_name": user.full_name,
            "is_student_mirea": str(user.is_student_mirea),
            "group": user.group
        })
        await redis.expire(user_key, 3600)

        await make_user_active(user.id)

        return {"message": "Пользователь успешно зарегистрирован"}

    except Exception as e:
        logger.error(f"Ошибка при регистрации пользователя на хакатон: {e}")
        raise


@router.get("/register", response_model=Union[SUserCheckRegistration, ErrorResponse],
            responses={400: {"model": ErrorResponse}})
@exception_handler
async def check_registration(user: SUser = Depends(fast_auth_user)) -> SUserCheckRegistration:
    """Проверяет зарегистрирован ли пользователь в приложении"""
    if user:
        status = True
    else:
        status = False
    return SUserCheckRegistration(is_user_registered_for_hackathon=status)


@router.get("/my_profile", response_model=Union[ProfileInfo, ErrorResponse],
            responses={400: {"model": ErrorResponse}})
@exception_handler
async def get_my_profile(session: AsyncSession = Depends(db.get_db),
                         user: SUser = Depends(fast_auth_user)) -> ProfileInfo:
    """Получает информацию о пользователе и его команде"""
    try:
        team = await TeamDAO.find_team_with_members_by_user_id(session=session, user_id=user.get('id'))

        user_info = SUserInfo(
            id=user.get('id'),
            username=user.get('username'),
            first_name=user.get('first_name'),
            last_name=user.get('last_name')
        )

        team_info = STeam(
            id=team.id,
            name=team.name,
            is_open=team.is_open,
            description=team.description,
            hackathon_id=team.hackathon_id
        ) if team else None

        if user.get('last_active') is not None:
            await make_user_active(user_id=str(user.get('telegram_id')))

        return ProfileInfo(user=user_info, team=team_info)
    except Exception as e:
        logger.error(f"Ошибка при получении профиля пользователя: {e}")
        raise
