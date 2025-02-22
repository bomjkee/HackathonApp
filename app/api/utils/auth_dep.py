from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
from fastapi.responses import Response

from app.db.dao import UserDAO
from config import settings, admins, redis
from app.db.session_maker_fast_api import db
from app.api.typization.schemas import TelegramIDModel
from app.api.typization.responses import SUser
from app.api.utils.redis_operations import redis_data, make_user_active
from app.api.typization.exceptions import NoUserIdException, ForbiddenException, UserNotFoundException, AuthException
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
        user_data = await redis_data(dict_data["user"]["id"])
        return user_data
    else:
        raise AuthException


