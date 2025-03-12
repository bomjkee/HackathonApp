from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config import logger
from app.db.dao import UserDAO
from app.db.session_maker import db
from app.api.typization.schemas import TelegramIDModel
from app.api.utils.redis_operations import redis_data
from app.api.typization.exceptions import  AuthException
from app.api.utils.api_utils import authorization_check



async def get_authenticated_user(request: Request, session: AsyncSession = Depends(db.get_db)):
    headers = dict(request.headers)
    authorization_status, dict_data = await authorization_check(headers)

    if authorization_status:
        return await UserDAO.find_one_or_none(session=session,
                                              filters=TelegramIDModel(telegram_id=dict_data["user"]["id"]))
    else:
        raise AuthException


async def fast_auth_user(request: Request):
    headers = dict(request.headers)
    authorization_status, dict_data = await authorization_check(headers)

    if authorization_status:
        user_data = await redis_data(tg_id=dict_data["user"]["id"])
        logger.info(f"Аутентификация пользователя {dict_data["user"]["username"]}")
        return user_data
    else:
        raise AuthException


