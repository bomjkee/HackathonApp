from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config import logger
from app.db.dao import UserDAO
from app.db.session_maker import db
from app.api.typization.schemas import TelegramIDModel
from app.redis.redis_operations.user import redis_user_data
from app.api.typization.exceptions import AuthException, UserNotFoundException
from app.api.utils.api_utils import authorization_check, exception_handler


async def get_authenticated_user(request: Request, session: AsyncSession = Depends(db.get_db)):
    headers = dict(request.headers)
    authorization_status, dict_data = await authorization_check(headers)

    if authorization_status:
        return await UserDAO(session).find_one_or_none(filters=TelegramIDModel(telegram_id=dict_data["user"]["id"]))
    else:
        raise AuthException


async def fast_auth_user(request: Request):
    """ Быстрая аутентификация пользователя """
    try:
        headers = dict(request.headers)
        authorization_status, dict_data = await authorization_check(headers)

        if authorization_status and dict_data:
            logger.info(f"Аутентификация пользователя {dict_data["user"]["username"]}")

            user_data = await redis_user_data(tg_id=dict_data["user"]["id"])
            if not user_data:
                raise UserNotFoundException()

            return user_data

        raise AuthException

    except Exception as e:
        logger.error(f"Ошибка при аутентификации пользователя: {e}")
        raise

