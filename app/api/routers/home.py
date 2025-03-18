from typing import Union
from fastapi import APIRouter, Depends
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.redis.custom_redis import CustomRedis
from app.redis.redis_client import get_redis
from app.redis.redis_operations.user import redis_user_data, get_teams_data_by_user, invalidate_user_cache
from app.api.typization.exceptions import UserNotFoundException, UserAlreadyExistsException
from app.db.dao import UserDAO
from app.api.utils.api_utils import exception_handler, check_registration_for_app, generate_response_model
from app.api.utils.auth_dep import fast_auth_user

from app.api.typization.schemas import UserInfoUpdate, IdModel
from app.api.typization.responses import SUser, ErrorResponse, SUserInfo, ProfileInfo, SUserCheckRegistration, \
    SuccessResponse
from app.db.session_maker import db

router = APIRouter(tags=["Работа с пользователем и Telegram"])


@router.post(
    path="/register",
    summary="Зарегистрировать пользователя в приложении",
    response_model=Union[SuccessResponse, ErrorResponse],
    responses={
        200: generate_response_model(description="Успешный запрос. Возвращает сообщение об успешной регистрации",
                                     model=SuccessResponse),
        401: generate_response_model("Ошибка авторизации"),
        404: generate_response_model("Пользователь не найден"),
        409: generate_response_model("Пользователь уже зарегистрирован"),
        422: generate_response_model("Ошибка валидации входных данных"),
        500: generate_response_model()
    }
)
@exception_handler
async def register_user(
        user_info: UserInfoUpdate,
        session: AsyncSession = Depends(db.get_db_with_commit),
        redis: CustomRedis = Depends(get_redis),
        user: SUser = Depends(fast_auth_user)
) -> SuccessResponse:
    """Регистрирует пользователя в приложении, обновляя запись в бд.
    Пользователь считается зарегистрированным, если у него есть обязательные поля ФИО и
    является ли он студентом МИРЭА, опционально учебная группа
    """
    try:

        is_registered = check_registration_for_app(user=user)
        if is_registered:
            raise UserAlreadyExistsException

        await UserDAO(session).update(filters=IdModel(id=user.get("id")), values=user_info)

        await invalidate_user_cache(redis=redis, tg_id=user.telegram_id, invalidate_user=True)

        await redis_user_data(tg_id=user.telegram_id)

        return SuccessResponse(message="Пользователь успешно зарегистрирован")

    except Exception as e:
        logger.error(f"Ошибка при регистрации пользователя на хакатон: {e}")
        raise


@router.get(
    path="/register",
    summary="Проверить регистрацию пользователя в приложении",
    response_model=Union[SUserCheckRegistration, ErrorResponse],
    responses={
        200: generate_response_model(
            description="Успешный запрос. Возвращает зарегистрирован ли пользователь",
            model=SUserCheckRegistration),
        401: generate_response_model("Ошибка авторизации"),
        404: generate_response_model("Пользователь не найден"),
        500: generate_response_model()
    }
)
@exception_handler
async def check_registration(user: SUser = Depends(fast_auth_user)) -> SUserCheckRegistration:
    """Проверяет зарегистрирован ли пользователь в приложении"""
    try:

        is_registered = check_registration_for_app(user=user)

        return SUserCheckRegistration(is_registered=is_registered)

    except Exception as e:
        logger.error(f"Ошибка при проверке регистрации пользователя: {e}")
        raise


@router.get(
    path="/my_profile",
    response_model=Union[ProfileInfo, ErrorResponse],
    summary="Получить профиль пользователя (только при наличии регистрации)",
    responses={
        200: generate_response_model(description="Успешный запрос. Возвращает информацию профиля",
                                     model=ProfileInfo),
        401: generate_response_model("Ошибка авторизации"),
        404: generate_response_model("Пользователь не найден"),
        409: generate_response_model("Пользователь уже зарегистрирован"),
        500: generate_response_model()
    }
)
@exception_handler
async def get_my_profile(
        session: AsyncSession = Depends(db.get_db),
        redis: CustomRedis = Depends(get_redis),
        user: SUser = Depends(fast_auth_user)
) -> ProfileInfo:
    """Получает информацию профиля пользователя: данные из telegram и команды,
    в которых состоит пользователь"""
    try:

        user_info = SUserInfo(
            username=user.username,
            first_name=user.first_name or "",
            last_name=user.last_name or ""
        )

        teams_by_user = await get_teams_data_by_user(redis=redis, session=session, user_id=user.telegram_id)

        return ProfileInfo(user=user_info, teams=teams_by_user)

    except Exception as e:
        logger.error(f"Ошибка при получении профиля пользователя: {e}")
        raise
