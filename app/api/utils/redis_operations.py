from typing import Dict, Union, Tuple
import time
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.api.typization.responses import SMember
from app.db.dao import UserDAO, MemberDAO
from app.api.typization.schemas import IdModel
from app.db.session_maker_fast_api import db
from config import redis


async def redis_data(user_id: int, session: AsyncSession = Depends(db.get_db)) -> dict | None:
    """
    Retrieves user data from Redis. If not found, fetches from the database,
    stores in Redis, and returns the data.
    """
    key = f"user_info:{user_id}"
    try:
        user_data = await redis.hgetall(key)
        new_info = False

        if not user_data:
            user = await UserDAO.find_one_or_none(session=session, filters=IdModel(id=user_id))
            logger.info("User not in redis")
            if user is None:
                return None
            user_data = {
                "id": user.id,
                "telegram_id": user.telegram_id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "last_active": str(time.time())
            }

            await redis.hset(key, mapping=user_data)
            await redis.expire(key, 3600)

            user_data = convert_redis_data(user_data)

        return user_data
    except Exception as e:
        logger.error(f"Ошибка при получении пользователя: {e}")
        return None


async def make_user_active(user_id: str) -> None:
    """
    Обновляет last_active текущего пользователя.
    """
    key = f"user_info:{user_id}"

    user_data = await redis.hgetall(key)
    if user_data:
        await redis.hset(key, "last_active", str(time.time()))
        await redis.expire(key, 3600)


def convert_redis_data(data: Dict[str, str]) -> Dict[str, Union[str, int, float]]:
    """
    Converts Redis data (which are all strings) to appropriate Python types
    (int, float, str) where possible.
    """
    converted_data = {}
    for key, value in data.items():
        try:
            converted_data[key] = int(value)
        except ValueError:
            try:
                converted_data[key] = float(value)
            except ValueError:
                converted_data[key] = value
    return converted_data


async def is_user_registered_for_hackathon(user_id: int, hackathon_id: int, session: AsyncSession) -> bool:
    """Checks if user is registered for a hackathon (indirectly via team membership)."""
    redis_key = f"hackathon_registration:{hackathon_id}:{user_id}"
    try:
        is_registered = await redis.get(redis_key)
        if is_registered is not None:
            return is_registered == "true"

        count = await MemberDAO.count(
            session=session,
            filters=SMember(user_id=user_id, hackathon_id=hackathon_id)
        )
        is_registered = count > 0

        await set_hackathon_registration_status(user_id, hackathon_id, is_registered)
        return is_registered

    except Exception as e:
        logger.error(f"Ошибка при проверке регистрации пользователя: {e}")
        return False


async def set_hackathon_registration_status(user_id: int, hackathon_id: int, is_registered: bool) -> None:
    """
    Sets the hackathon registration status in Redis.
    """
    redis_key = f"hackathon_registration:{hackathon_id}:{user_id}"
    try:
        if is_registered:
            await redis.set(redis_key, "true", ex=3600)
            logger.info(
                f"Set hackathon registration status in Redis for user {user_id} and hackathon {hackathon_id} to True")
        else:
            await redis.set(redis_key, "false", ex=3600)
            logger.info(
                f"Set hackathon registration status in Redis for user {user_id} and hackathon {hackathon_id} to False")

    except Exception as e:
        logger.error(f"Error setting hackathon registration status in Redis: {e}")
