from typing import List
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.redis.custom_redis import CustomRedis
from app.redis.redis_client import redis_client
from app.api.typization.responses import SUser,  STeam
from app.db.dao import UserDAO, TeamDAO
from app.api.typization.schemas import TelegramIDModel
from app.db.session_maker import db



async def redis_user_data(tg_id: int) -> SUser | None:
    try:

        redis: CustomRedis = redis_client.get_client()

        async for session in db.get_db():
            user_cache_key = f"user:{tg_id}"

            user_data = await redis.get_cached_data(cache_key=user_cache_key,
                                                    fetch_data_func=UserDAO(session).find_one_or_none,
                                                    model=SUser,
                                                    filters=TelegramIDModel(telegram_id=tg_id))
            if not user_data:
                logger.error(f"Пользователь с ID {tg_id} не найден.")
                return None

            return user_data

    except Exception as e:
        logger.error(f"Общая ошибка при получении пользователя: {e}")
        return None



async def get_teams_data_by_user(redis: CustomRedis, session: AsyncSession, user_id: int) -> List[STeam] | None:
    try:

        team_user_cache_key = f"teams:user:{user_id}"

        team_data = await redis.get_cached_data(cache_key=team_user_cache_key,
                                                fetch_data_func=TeamDAO(session).find_all_teams_by_user_id,
                                                model=STeam,
                                                user_id=user_id,
                                                ttl=7200, )

        if team_data is None:
            logger.error(f"Команда пользователя с ID {user_id} не найдена.")
            return None

        return team_data

    except Exception as e:
        logger.error(f"Ошибка при получении команды пользователя с ID {user_id}: {e}")
        return None



async def invalidate_user_cache(
        redis: CustomRedis,
        tg_id: int,
        invalidate_teams: bool = False,
        invalidate_user: bool = False,
        user_info: SUser | None = None
) -> None:

    if invalidate_user:
        user_key = f"user:{tg_id}"
        await redis.delete_key(user_key)

    if invalidate_teams:
        user_teams_cache_key = f"teams:user:{tg_id}"
        await redis.delete_key(user_teams_cache_key)
