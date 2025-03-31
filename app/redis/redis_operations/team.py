import json
from typing import List
from loguru import logger
from sqlalchemy import false
from sqlalchemy.ext.asyncio import AsyncSession

from app.redis.custom_redis import CustomRedis
from app.redis.redis_operations.member import get_member_data_by_team_id
from app.api.typization.exceptions import TeamNotFoundException, ForbiddenException
from app.api.typization.responses import STeam
from app.db.dao import TeamDAO
from app.api.typization.schemas import IdModel, HackathonIDModel



async def get_all_teams_data(
        redis: CustomRedis,
        session: AsyncSession,
        find_by_hackathon: bool = False,
        hackathon_id: int | None = None
) -> List[STeam] | None:
    try:

        teams_cache_key = f"teams"
        filters = None

        if find_by_hackathon and hackathon_id:
            teams_cache_key += f":hackathon:{hackathon_id}"
            filters = HackathonIDModel(hackathon_id=hackathon_id)

        teams_data = await redis.get_cached_data(cache_key=teams_cache_key,
                                             fetch_data_func=TeamDAO(session).find_all,
                                             model=STeam,
                                             filters=filters)

        if teams_data is None:
            logger.error(f"Команды не найдены.")
            return None

        return teams_data

    except Exception as e:
        logger.error(f"Ошибка при получении команд: {e}")
        return None



async def get_team_data(redis: CustomRedis, session: AsyncSession, team_id: int) -> STeam | None:
    try:

        team_cache_key = f"team:{team_id}"

        team_data = await redis.get_cached_data(cache_key=team_cache_key,
                                                fetch_data_func=TeamDAO(session).find_one_or_none,
                                                model=STeam,
                                                filters=IdModel(id=team_id))

        if team_data is None:
            logger.error(f"Команда с ID {team_id} не найдена.")
            return None

        return team_data

    except Exception as e:
        logger.error(f"Ошибка при получении команды: {e}")
        return None


async def get_team_if_user_is_leader(
        redis: CustomRedis,
        session: AsyncSession,
        team_id: int,
        user_id: int
) -> STeam:
    try:

        existing_team = await get_team_data(redis=redis, session=session, team_id=team_id)
        if not existing_team:
            raise TeamNotFoundException

        leader = await get_member_data_by_team_id(redis=redis, session=session, team_id=existing_team.id, role="leader")
        if not leader or leader.user_id != user_id:
            raise ForbiddenException

        return existing_team

    except Exception as e:
        logger.error(f"Ошибка при получении команды лидера: {e}")
        raise



async def invalidate_team_cache(
        redis: CustomRedis,
        hackathon_id: int | None = None,
        team_id: int | None = None,
        team: STeam | None = None
) -> None:

    if hackathon_id:
        team_list_cache_key = "teams"
        await redis.delete_key(team_list_cache_key)

        teams_for_hackathon_cache_key = f"teams:hackathon:{hackathon_id}"
        await redis.delete_key(teams_for_hackathon_cache_key)

    if team_id:
        team_cache_key = f"team:{team_id}"
        await redis.delete_key(team_cache_key)

        if team:
            await redis.set_value_with_ttl(key=team_cache_key, value=json.dumps(team.model_dump()))

