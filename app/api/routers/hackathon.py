import json
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Union

from config import redis, logger
from app.db.dao import HackathonDAO
from app.db.session_maker import db
from app.api.utils.auth_dep import fast_auth_user
from app.api.utils.api_utils import exception_handler
from app.api.utils.redis_operations import convert_redis_data, get_hackathon_by_id_from_redis
from app.api.typization.responses import SHackathonInfo, SHackathons, SUser, ErrorResponse
from app.api.typization.schemas import IdModel
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
    try:
        hackathon = await get_hackathon_by_id_from_redis(session=session, hackathon_id=hackathon_id)
        return hackathon
    except Exception as e:
        logger.error(f"Ошибка при получении информации о хакатоне: {e}")
        raise


