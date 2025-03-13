from typing import Union
from fastapi import APIRouter, Depends
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.typization.exceptions import UserNotFoundException, UserAlreadyExistsException
from app.db.dao import UserDAO, TeamDAO
from app.api.utils.api_utils import exception_handler
from app.api.utils.auth_dep import fast_auth_user

from app.api.typization.schemas import UserInfoUpdate, IdModel
from app.api.typization.responses import SUser, ErrorResponse, SUserInfo, STeam, ProfileInfo, SUserCheckRegistration, SuccessResponse
from app.db.session_maker import db
from config import redis

router = APIRouter(tags=["Работа с пользователем и Telegram"])


@router.post("/register", response_model=Union[SuccessResponse, ErrorResponse],
             responses={400: {"model": ErrorResponse}})
@exception_handler
async def register_user(user_info: UserInfoUpdate,
                        session: AsyncSession = Depends(db.get_db_with_commit),
                        user: SUser = Depends(fast_auth_user)) -> SuccessResponse:
    """Регистрирует пользователя (обновляет запись в бд и дописывает фио и группу опционально)"""
    try:
        is_registered = bool(user.get("full_name") not in ["", " ", "<null>"])
        if is_registered:
            raise UserAlreadyExistsException

        update_status = await UserDAO.update(session=session, filters=IdModel(id=user.get("id")), values=user_info)
        if update_status != 1:
            raise UserNotFoundException

        user_key = f"user_info:{user.get("telegram_id")}"

        await redis.hset(user_key, mapping={
            "full_name": user_info.full_name,
            "is_mirea_student": str(user_info.is_mirea_student),
            "group": user_info.group or ""
        })
        await redis.expire(user_key, 3600)

        return SuccessResponse(message="Пользователь успешно зарегистрирован")


    except Exception as e:
        logger.error(f"Ошибка при регистрации пользователя на хакатон: {e}")
        raise


@router.get("/register", response_model=Union[SUserCheckRegistration, ErrorResponse],
            responses={400: {"model": ErrorResponse}})
@exception_handler
async def check_registration(user: SUser = Depends(fast_auth_user)) -> SUserCheckRegistration:
    """Проверяет зарегистрирован ли пользователь в приложении"""
    try:
        is_registered = bool(user.get("full_name") not in ["", "<null>"])

        return SUserCheckRegistration(is_registered=is_registered)
    except Exception as e:
        logger.error(f"Ошибка при проверке регистрации пользователя: {e}")
        raise



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

        team_info = STeam(**team.to_dict()) if team else None

        return ProfileInfo(user=user_info, team=team_info)

    except Exception as e:
        logger.error(f"Ошибка при получении профиля пользователя: {e}")
        raise
