from typing import List
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.redis.custom_redis import CustomRedis
from app.redis.redis_operations.team import invalidate_team_cache
from app.api.typization.responses import SHackathonInfo, SHackathons
from app.db.dao import HackathonDAO
from app.api.typization.schemas import IdModel



async def get_all_hackathons_data(redis: CustomRedis, session: AsyncSession) -> List[SHackathons] | None:
    try:

        hackathons_cache_key = "hackathons"

        hackathons_data = await redis.get_cached_data(cache_key=hackathons_cache_key,
                                                      fetch_data_func=HackathonDAO(session).find_all,
                                                      model=SHackathons)

        if hackathons_data is None:
            logger.warning(f"Хакатоны не найдены.")
            return None

        return hackathons_data

    except Exception as e:
        logger.error(f"Ошибка при получении хакатонов: {e}")
        return None



async def get_hackathon_data(redis: CustomRedis, session: AsyncSession, hackathon_id: int) -> SHackathonInfo | None:
    try:

        hackathon_cache_key = f"hackathon:{hackathon_id}"

        hackathon_data = await redis.get_cached_data(cache_key=hackathon_cache_key,
                                                     fetch_data_func=HackathonDAO(session).find_one_or_none,
                                                     model=SHackathonInfo,
                                                     filters=IdModel(id=hackathon_id))

        if hackathon_data is None:
            logger.warning(f"Хакатон c {hackathon_id} не найден.")
            return None

        return hackathon_data

    except Exception as e:
        logger.error(f"Ошибка при получении хакатона: {e}")
        return None



async def invalidate_hackathon_data(redis: CustomRedis, hackathon_id: int, invalidate_teams: bool = False) -> None:

    hackathon_list_cache_key = "hackathons"
    await redis.delete_key(hackathon_list_cache_key)

    hackathon_cache_key = f"hackathon:{hackathon_id}"
    await redis.delete_key(hackathon_cache_key)

    if invalidate_teams:
        await invalidate_team_cache(redis=redis, hackathon_id=hackathon_id)
