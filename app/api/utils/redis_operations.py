from typing import Dict, Union
import time
from loguru import logger

from app.api.typization.responses import SMember, SUser
from app.db.dao import UserDAO, MemberDAO
from app.api.typization.schemas import IdModel, TelegramIDModel
from app.db.session_maker import db, DatabaseSession
from config import redis


async def redis_data(user_id: int) -> SUser | None:
    """
    Извлекает данные пользователя из Redis. Если не найдено, извлекает из базы данных,
    сохраняет в Redis и возвращает данные.
    """
    key = f"user_info:{user_id}"
    try:
        user_data = await redis.hgetall(key)

        if not user_data:
            async for session in DatabaseSession.get_db():

                user = await UserDAO.find_one_or_none(session=session, filters=TelegramIDModel(telegram_id=user_id))
                logger.info(f"Пользователь из базы данных")

                if user is None:
                    logger.error(f"Пользователь с ID {user_id} не найден.")
                    return None

                user_data = {
                    "id": user.id,
                    "telegram_id": user.telegram_id,
                    "first_name": user.first_name or "",
                    "last_name": user.last_name or "",
                    "username": user.username or "",
                    "last_active": int(time.time())
                }

            await redis.hset(key, mapping=user_data)
            await redis.expire(key, 3600)
        else:
            logger.info("Пользователь из Redis")
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
    Преобразует данные из Redis (все строки) в соответствующие типы Python
    (int, float, str), где это возможно.
    """
    converted_data = {}
    for key, value in data.items():
        if isinstance(key, bytes):
            key = key.decode()

        if isinstance(value, bytes):
            value = value.decode()

        try:
            converted_data[key] = int(value)
        except ValueError:
            try:
                converted_data[key] = float(value)
            except ValueError:
                converted_data[key] = value
    return converted_data
