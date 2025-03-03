from typing import Any, Tuple, Dict, Union
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.requests import Request
from fastapi.responses import Response, RedirectResponse

from app.db.dao import UserDAO, TeamDAO
from app.api.utils.api_utils import exception_handler
from app.api.utils.auth_dep import fast_auth_user, get_authenticated_user

from app.api.typization.schemas import TelegramIDModel
from app.api.typization.responses import SUser, ErrorResponse, SUserInfo, STeam, ProfileInfo
from app.db.session_maker_fast_api import db
from app.api.utils.redis_operations import redis_data, make_user_active

router = APIRouter()


@router.get("/my_profile", response_model=Union[ProfileInfo, ErrorResponse],
            responses={400: {"model": ErrorResponse}})
@exception_handler
async def get_my_profile(session: AsyncSession = Depends(db.get_db),
                         user: SUser = Depends(fast_auth_user)) -> ProfileInfo:
    """Получает информацию о пользователе и его команде"""
    try:
        team = await TeamDAO.find_team_with_members_by_user_id(session=session, user_id=user.id)

        user_info = SUserInfo(
            id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )

        team_info = STeam(
            id=team.id,
            name=team.name,
            is_open=team.is_open,
            description=team.description,
            hackathon_id=team.hackathon_id
        ) if team else None

        await make_user_active(user_id=str(user.id))

        return ProfileInfo(user=user_info, team=team_info)
    except Exception as e:
        logger.error(f"Ошибка при получении профиля пользователя: {e}")
        raise




