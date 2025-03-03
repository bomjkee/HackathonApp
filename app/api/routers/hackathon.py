import json
from fastapi import APIRouter, Depends
from pydantic_core import ErrorTypeInfo
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Union

from config import redis, logger
from app.db.dao import HackathonDAO, UserDAO
from app.db.session_maker_fast_api import db
from app.api.utils.auth_dep import fast_auth_user
from app.api.utils.api_utils import exception_handler
from app.api.utils.redis_operations import convert_redis_data, redis_data, is_user_registered_for_hackathon
from app.api.typization.responses import SHackathonInfo, SHackathons, SUser, ErrorResponse
from app.api.typization.schemas import IdModel, UserInfoUpdate
from app.api.typization.exceptions import HackathonNotFoundException, HackathonsNotFoundException, UserNotFoundException


router = APIRouter(prefix="/hackathons", tags=["Работа с хакатонами"])


@router.get("/", response_model=Union[List[SHackathons], ErrorResponse],
            responses={400: {"model": ErrorResponse}})
@exception_handler
async def get_all_hackathons(session: AsyncSession = Depends(db.get_db)) -> List[SHackathons]:
    """Получает информацию о хакатонах, используя Redis."""

    cache_key = "all_hackathons"
    try:
        await redis.delete(cache_key)
        cached_teams = await redis.get(cache_key)

        if cached_teams:
            hackathons_data = json.loads(cached_teams)
            logger.info(f"Хакатоны из Redis: {hackathons_data}")
            hackathons = [SHackathons(**convert_redis_data(hackathon_data)) for hackathon_data in hackathons_data]
            return hackathons
        else:
            hackathons = await HackathonDAO.find_all(session=session)
            if not hackathons:
                raise HackathonsNotFoundException

            hackathons_data = [SHackathons(id=hackathon.id, name=hackathon.name, start_description=hackathon.start_description) for hackathon in hackathons]
            await redis.set(cache_key, json.dumps([hackathon_data.model_dump() for hackathon_data in hackathons_data]))
            await redis.expire(cache_key, 3600)

            return hackathons_data

    except Exception as e:
        logger.error(f"Ошибка при получении информации о хакатонах: {e}")
        raise


@router.get("/{hackathon_id}", response_model=Union[SHackathonInfo, ErrorResponse],
            responses={400: {"model": ErrorResponse}})
@exception_handler
async def get_hackathon_by_id(hackathon_id: int, session: AsyncSession = Depends(db.get_db)) -> SHackathonInfo:
    """Получает информацию о хакатоне."""

    hackathon_cache_key = f"hackathon:{hackathon_id}"

    try:
        cached_team_data = await redis.get(hackathon_cache_key)

        if cached_team_data:
            hackathon_data = json.loads(cached_team_data)
            logger.info(f"Хакатон из Redis: {hackathon_data}")

            return SHackathonInfo(**convert_redis_data(hackathon_data))

        else:
            hackathon_data = await HackathonDAO.find_one_or_none(session=session, filters=IdModel(id=hackathon_id))
            if hackathon_data is None:
                raise HackathonNotFoundException

            hackathon = SHackathonInfo(**hackathon_data.to_dict())

            await redis.set(hackathon_cache_key, json.dumps(hackathon.model_dump()))
            await redis.expire(hackathon_cache_key, 3600)  # TTL = 1 час

            return hackathon

    except Exception as e:
        logger.error(f"Ошибка при получении информации о хакатоне: {e}")
        raise


@router.post("/{hackathon_id}/register", response_model=Union[dict, ErrorResponse],
             responses={400: {"model": ErrorResponse}})
@exception_handler
async def register_user_for_hackathon(hackathon_id: int,
                                      user_info: UserInfoUpdate,
                                      session: AsyncSession = Depends(db.get_db_with_commit),
                                      user: SUser = Depends(fast_auth_user)) -> dict:
    """Регистрирует пользователя на хакатон."""
    try:
        hackathon = await HackathonDAO.find_one_or_none(session=session, filters=IdModel(id=hackathon_id))
        if not hackathon:
            raise HackathonNotFoundException

        registration_status = await is_user_registered_for_hackathon(user_id=user.id, hackathon_id=hackathon.id, session=session)
        if registration_status:
            raise


        user = await UserDAO.update(session=session, filters=IdModel(id=user.id), values=user_info)
        if not user:
            raise UserNotFoundException



        user_key = f"user_info:{user.id}"
        await redis.hset(user_key, mapping={
            "full_name": user.full_name,
            "is_student_mirea": user.is_student_mirea,
            "group": user.group
        })
        await redis.expire(user_key, 3600)

        return {"message": "Пользователь успешно зарегистрирован"}

    except Exception as e:
        logger.error(f"Ошибка при регистрации пользователя на хакатон: {e}")
        raise