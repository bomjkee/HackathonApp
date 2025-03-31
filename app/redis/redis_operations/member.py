import json
from typing import List
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.redis.custom_redis import CustomRedis
from app.api.typization.responses import STeam, SMember
from app.db.dao import MemberDAO
from app.api.typization.schemas import MemberFind, HackathonIDModel


async def get_all_members_data(
        redis: CustomRedis,
        session: AsyncSession,
        team_id: int | None = None,
        hackathon_id: int | None = None
) -> List[SMember] | None:
    try:

        members_cache_key = f"members"
        filters = {}
        fetch_data = MemberDAO(session).find_all

        if team_id:
            members_cache_key += f":team:{team_id}"
            filters = MemberFind(team_id=team_id)

        members_data = await redis.get_cached_data(cache_key=members_cache_key,
                                                   fetch_data_func=fetch_data,
                                                   model=SMember,
                                                   filters=filters)

        if members_data is None:
            logger.error(f"Участники {f"команды с ID {team_id}" if team_id else ""} не найдены.")
            return None

        return members_data

    except Exception as e:
        logger.error(f"Ошибка при получении команды: {e}")
        return None



async def get_member_data_by_team_id(
        redis: CustomRedis,
        session: AsyncSession,
        team_id: int,
        user_id: int | None = None,
        role: str | None = None,
) -> SMember | None:
    try:

        member_cache_key = f"members:team:{team_id}"
        filters = MemberFind(team_id=team_id)

        if role == "leader":
            member_cache_key += f":leader"
            filters.role = role

        elif user_id:
            member_cache_key += f":member:{user_id}"
            filters.user_id = user_id

        else:
            logger.warning("Недостаточно параметров для поиска")
            return None

        member_data = await redis.get_cached_data(cache_key=member_cache_key,
                                                  fetch_data_func=MemberDAO(session).find_one_or_none,
                                                  model=SMember,
                                                  filters=filters)

        if member_data is None:
            logger.error(f"Участник команды с ID {team_id} не найден.")
            return None

        return member_data

    except Exception as e:
        logger.error(f"Ошибка при получении участника команды с ID {team_id}: {e}")
        return None



async def count_members_in_team(redis: CustomRedis, session: AsyncSession, team_id: int) -> int:
    try:

        members_data = await get_all_members_data(redis=redis, session=session, team_id=team_id)

        if members_data is None:
            logger.error(f"Участников в команде с ID {team_id} не найдено.")
            return 0

        return len(members_data)

    except Exception as e:
        logger.error(f"Ошибка при подсчете количества участников в команде: {e}")
        return 0



async def find_existing_member_by_hackathon(
        redis: CustomRedis,
        session: AsyncSession,
        user_id: int,
        hackathon_id: int
) -> SMember | None:
    try:

        members_data = await get_all_members_data(redis=redis, session=session, hackathon_id=hackathon_id)
        member = next((m for m in members_data if m.user_id == user_id), None)

        if member is not None:
            logger.info(f"Участник с user_id {user_id} и hackathon_id {hackathon_id} найден.")
        else:
            logger.info(f"Участник с user_id {user_id} и hackathon_id {hackathon_id} не найден.")

        return member

    except Exception as e:
        logger.error(f"Ошибка при поиске участника с user_id {user_id} и hackathon_id {hackathon_id}: {e}")
        return None



async def invalidate_member_cache(
        redis: CustomRedis,
        team_id: int,
        hackathon_id: int,
        invalidate_member: bool = False,
        invalidate_leader: bool = False,
        tg_id: int | None = None,
        member: SMember | None = None
) -> None:

    member_list_cache_key = "members"
    await redis.delete_key(member_list_cache_key)

    members_hackathon_cache_key = f"members:hackathon:{hackathon_id}"
    await redis.delete_key(members_hackathon_cache_key)

    members_team_cache_key = f"members:team:{team_id}"
    await redis.delete_key(members_team_cache_key)

    if tg_id:
        member_cache_key = f"members:team:{team_id}:member:{tg_id}"

        if invalidate_member:
            await redis.delete_key(member_cache_key)

        if member:
            await redis.set_value_with_ttl(key=member_cache_key, value=json.dumps(member.model_dump()))

    if invalidate_leader:
        leader_cache_key = f"members:team:{team_id}:leader"
        await redis.delete_key(leader_cache_key)

