from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Union
from loguru import logger

from app.redis.custom_redis import CustomRedis
from app.redis.redis_client import get_redis
from app.api.typization.exceptions import HackathonsNotFoundException, HackathonNotFoundException
from app.db.session_maker import db
from app.api.utils.api_utils import exception_handler, generate_response_model
from app.redis.redis_operations.hackathon import get_all_hackathons_data, get_hackathon_data
from app.api.typization.responses import SHackathonInfo, SHackathons, ErrorResponse

router = APIRouter(prefix="/hackathons", tags=["Работа с хакатонами"])


@router.get(
    path="/",
    summary="Получить список хакатонов",
    response_model=Union[List[SHackathons], ErrorResponse],
    responses={
        200: generate_response_model(description="Успешный запрос. Возвращает список хакатонов",
                                     model=List[SHackathons]),
        404: generate_response_model("Хакатоны не найдены"),
        500: generate_response_model()}
)
@exception_handler
async def get_all_hackathons(
        session: AsyncSession = Depends(db.get_db),
        redis: CustomRedis = Depends(get_redis)
) -> List[SHackathons]:
    """Получить информацию о хакатонах"""
    try:

        hackathons = await get_all_hackathons_data(redis=redis, session=session)
        if not hackathons:
            raise HackathonsNotFoundException

        return hackathons

    except Exception as e:
        logger.error(f"Ошибка при получении информации о хакатонах: {e}")
        raise


@router.get(
    path="/{hackathon_id}",
    summary="Получить информацию о хакатоне по ID",
    response_model=Union[SHackathonInfo, ErrorResponse],
    responses={
        200: generate_response_model(description="Успешный запрос. Возвращает хакатон", model=SHackathonInfo),
        404: generate_response_model("Хакатон не найден"),
        422: generate_response_model("Ошибка валидации входных данных"),
        500: generate_response_model()
    }
)
@exception_handler
async def get_hackathon_by_id(
        hackathon_id: int,
        session: AsyncSession = Depends(db.get_db),
        redis: CustomRedis = Depends(get_redis)
) -> SHackathonInfo:
    """Получает информацию о хакатоне."""
    try:

        hackathon = await get_hackathon_data(redis=redis, session=session, hackathon_id=hackathon_id)
        if not hackathon:
            raise HackathonNotFoundException

        return hackathon

    except Exception as e:
        logger.error(f"Ошибка при получении информации о хакатоне: {e}")
        raise
