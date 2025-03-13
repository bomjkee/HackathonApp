from typing import Dict, Union
import time
import json
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.typization.exceptions import HackathonNotFoundException, TeamNotFoundException, InvitationNotFoundException
from app.api.typization.responses import SUser, SHackathonInfo, STeam, SInvite
from app.db.dao import UserDAO, MemberDAO, HackathonDAO, InviteDAO, TeamDAO
from app.api.typization.schemas import TelegramIDModel, IdModel
from app.db.session_maker import db, DatabaseSession
from config import redis


async def redis_data(tg_id: int) -> SUser | None:
    """
    Извлекает данные пользователя из Redis. Если не найдено, извлекает из базы данных,
    сохраняет в Redis и возвращает данные.
    """
    key = f"user_info:{tg_id}"
    try:
        user_data = await redis.hgetall(key)

        if not user_data:
            async for session in DatabaseSession.get_db():

                user = await UserDAO.find_one_or_none(session=session, filters=TelegramIDModel(telegram_id=tg_id))
                logger.info(f"Пользователь из базы данных")

                if user is None:
                    logger.error(f"Пользователь с ID {tg_id} не найден.")
                    return None

                user_data = {
                    "id": user.id,
                    "telegram_id": user.telegram_id,
                    "first_name": user.first_name or "",
                    "last_name": user.last_name or "",
                    "username": user.username or "",
                    "full_name": user.full_name or "",
                    "is_mirea_student": str(user.is_mirea_student) or "",
                    "group": user.group or "",
                    "last_active": int(time.time())
                }

            await redis.hset(key, mapping=user_data)
            await redis.expire(key, 3600)
        else:
            logger.info("Пользователь из Redis")
            user_data = convert_redis_data(user_data)
            await make_user_active(tg_id=str(user_data.get("telegram_id")))

        return user_data

    except Exception as e:
        logger.error(f"Ошибка при получении пользователя: {e}")
        return None


async def make_user_active(tg_id: str) -> None:
    """
    Обновляет last_active текущего пользователя.
    """
    key = f"user_info:{tg_id}"
    user_data = await redis.hgetall(key)
    if user_data:
        logger.info(f"Обновление в Redis последней активности пользователя {user_data.get("username")}")
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


async def get_hackathon_by_id_from_redis(session: AsyncSession, hackathon_id: int) -> SHackathonInfo:
    hackathon_cache_key = f"hackathon:{hackathon_id}"
    cached_hackathon_data = await redis.get(hackathon_cache_key)

    if cached_hackathon_data:
        hackathon_data = json.loads(cached_hackathon_data)
        logger.info(f"Хакатон из Redis: {hackathon_data}")

        hackathon = SHackathonInfo(**convert_redis_data(hackathon_data))
    else:
        hackathon_row = await HackathonDAO.find_one_or_none(session=session, filters=IdModel(id=hackathon_id))
        if hackathon_row is None:
            raise HackathonNotFoundException

        hackathon = SHackathonInfo(**hackathon_row.to_dict())

        await redis.set(hackathon_cache_key, json.dumps(hackathon.model_dump()))
        await redis.expire(hackathon_cache_key, 3600)

    return hackathon


async def get_team_by_id_from_redis(session: AsyncSession, team_id: int) -> STeam:
    team_cache_key = f"team:{team_id}"
    cached_team_data = await redis.get(team_cache_key)

    if cached_team_data:
        team_data = json.loads(cached_team_data["team"])
        logger.info(f"Команда из Redis: {team_data}")

        team = STeam(**convert_redis_data(team_data))
    else:
        team_row = await TeamDAO.find_one_or_none(session=session, filters=IdModel(id=team_id))
        if team_row is None:
            raise TeamNotFoundException

        team = STeam(**team_row.to_dict())

    return team


async def get_invite_by_id_from_redis(session: AsyncSession, invite_id: int) -> SInvite:
    invite_cache_key = f"invite:{invite_id}"
    invite_data = await redis.get(invite_cache_key)

    if invite_data:
        invite_data = json.loads(invite_data)
        logger.info(f"Приглашение из Redis: {invite_data}")

        invite = SInvite(**convert_redis_data(invite_data))
    else:
        invite_row = await InviteDAO.find_one_or_none(session=session, filters=IdModel(id=invite_id))
        if not invite_row:
            raise InvitationNotFoundException

        invite = SInvite(**invite_row.to_dict())

        await redis.set(invite_cache_key, json.dumps(invite.model_dump()))
        await redis.expire(invite_cache_key, 3600)

    return invite
