import json
from loguru import logger
from typing import Union, List
from aiogram.exceptions import TelegramForbiddenError
from fastapi import APIRouter, Depends, Body, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.utils.bot_utils import send_invite_to_user
from app.db.models import Invite
from app.redis.custom_redis import CustomRedis
from app.redis.redis_client import get_redis
from app.redis.redis_operations.member import get_all_members_data, find_existing_member_by_hackathon, \
    invalidate_member_cache, count_members_in_team
from app.redis.redis_operations.team import get_all_teams_data, get_team_data, \
    get_member_data_by_team_id, get_team_if_user_is_leader, invalidate_team_cache
from app.redis.redis_operations.hackathon import get_hackathon_data
from app.redis.redis_operations.invite import get_all_invites_user_data, invalidate_invite_cache
from app.redis.redis_operations.user import invalidate_user_cache, redis_user_data
from app.bot.keyboards.user_keyboards import invite_keyboard
from app.api.typization.schemas import IdModel, NameModel, TeamCreate, InviteCreate, MemberCreate, TeamUpdate
from app.api.typization.responses import STeam, SUser, ErrorResponse, STeamWithMembers, SuccessResponse, SMember, \
    SUserIsLeader
from app.api.typization.exceptions import (TeamNotFoundException, TeamsNotFoundException,
                                           TeamNameAlreadyExistsException, MaxTeamMembersExceededException,
                                           InvitationAlreadyExistsException, MemberNotFoundException,
                                           UserNotFoundException, MemberInTeamException, TeamCloseException,
                                           UserNotRegisteredToApp, HackathonNotFoundException, TeamEmptyException,
                                           ForbiddenException)
from app.api.utils.auth_dep import fast_auth_user
from app.api.utils.api_utils import exception_handler, check_registration_for_app, generate_response_model
from app.db.dao import TeamDAO, MemberDAO, InviteDAO
from app.db.models import Team
from app.db.session_maker import db
from config import bot

router = APIRouter(prefix="/teams", tags=["Работа с командами"])


@router.get(
    path="/",
    summary="Получить список команд",
    response_model=Union[List[STeam], ErrorResponse],
    responses={
        200: generate_response_model(description="Успешный запрос. Возвращает список команд", model=List[STeam]),
        404: generate_response_model("Команды не найдены"),
        500: generate_response_model()
    }
)
@exception_handler
async def get_all_teams(
        session: AsyncSession = Depends(db.get_db),
        redis: CustomRedis = Depends(get_redis)
) -> List[STeam]:
    """Получает информацию о командах"""
    try:

        teams = await get_all_teams_data(redis=redis, session=session)
        if not teams:
            raise TeamsNotFoundException

        return teams

    except Exception as e:
        logger.error(f"Ошибка при получении команд: {e}")
        raise


@router.get(
    path="/{team_id}",
    summary="Получить команду по ID и ее участников (опционально)",
    response_model=Union[STeamWithMembers, ErrorResponse],
    responses={
        200: generate_response_model(
            description="Успешный запрос. Возвращает информацию о команде и ее участниках (или же вместо участников null)",
            model=STeamWithMembers),
        404: generate_response_model("Команда не найдена или в ней нет участников"),
        422: generate_response_model("Ошибка валидации входных данных"),
        500: generate_response_model()
    }
)
@exception_handler
async def get_team_with_members_by_id(
        team_id: int,
        session: AsyncSession = Depends(db.get_db),
        redis: CustomRedis = Depends(get_redis)
) -> STeamWithMembers:
    """Получает информацию о команде с ее участниками."""
    try:

        team = await get_team_data(redis=redis, session=session, team_id=team_id)
        if not team:
            raise TeamNotFoundException

        members_in_team = await get_all_members_data(redis=redis, session=session, team_id=team_id)
        if not members_in_team:
            raise MemberNotFoundException

        return STeamWithMembers(team=team, members=members_in_team)

    except Exception as e:
        logger.error(f"Ошибка при получении информации о команде: {e}")
        raise


@router.post(
    path="/",
    summary="Создать новую команду",
    response_model=Union[SuccessResponse, ErrorResponse],
    responses={
        200: generate_response_model(description="Успешный запрос. Возвращает сообщение об успешном создании команды",
                                     model=SuccessResponse),
        401: generate_response_model("Ошибка авторизации"),
        404: generate_response_model("Пользователь не зарегистрирован в приложении или не найден"),
        409: generate_response_model("Имя команды уже существует или пользователь уже является участником команды"),
        422: generate_response_model("Ошибка валидации входных данных"),
        500: generate_response_model()
    }
)
@exception_handler
async def create_team(
        team: TeamCreate,
        session: AsyncSession = Depends(db.get_db_with_commit),
        redis: CustomRedis = Depends(get_redis),
        user: SUser = Depends(fast_auth_user)
) -> SuccessResponse:
    """Создает новую команду и очищает кэш"""

    try:

        is_register = check_registration_for_app(user=user)
        if not is_register:
            raise UserNotRegisteredToApp

        team_dao = TeamDAO(session)

        existing_team = await team_dao.find_one_or_none(filters=NameModel(name=team.name))
        if existing_team:
            raise TeamNameAlreadyExistsException

        member_for_hackathon = await MemberDAO(session).find_existing_member(user_id=user.telegram_id, hackathon_id=team.hackathon_id)
        if member_for_hackathon:
            raise MemberInTeamException

        new_team: Team = await team_dao.add(values=team)

        await MemberDAO(session).add(values=MemberCreate(
            user_id=user.telegram_id,
            tg_name=user.username,
            team_id=new_team.id,
            role="leader"
        ))

        await invalidate_team_cache(redis=redis, hackathon_id=team.hackathon_id, team=STeam(**new_team.to_dict()))
        await invalidate_user_cache(redis=redis, tg_id=user.telegram_id, invalidate_teams=True)

        await redis.set_value_with_ttl(key=f"team:{new_team.id}", value=json.dumps(new_team.to_dict()))

        return SuccessResponse(message="Команда была успешно создана")

    except Exception as e:
        logger.error(f"Ошибка при создании команды: {e}")
        raise


@router.patch(
    path="/{team_id}",
    summary="Обновить команду по ID (только лидером)",
    response_model=Union[SuccessResponse, ErrorResponse],
    responses={
        200: generate_response_model(description="Успешный запрос. Возвращает сообщение об успешном обновлении команды",
                                     model=SuccessResponse),
        401: generate_response_model("Ошибка авторизации"),
        403: generate_response_model("Пользователь не является лидером данной команды"),
        404: generate_response_model("Пользователь не найден"),
        409: generate_response_model("Имя команды уже существует"),
        422: generate_response_model("Ошибка валидации входных данных"),
        500: generate_response_model()
    }
)
@exception_handler
async def update_team(
        team_id: int,
        team: TeamUpdate,
        session: AsyncSession = Depends(db.get_db_with_commit),
        redis: CustomRedis = Depends(get_redis),
        user: SUser = Depends(fast_auth_user)
) -> SuccessResponse:
    """Обновляет информацию о команде и очищает кэш"""

    try:

        team_dao = TeamDAO(session)

        existing_team = await get_team_if_user_is_leader(
            redis=redis,
            session=session,
            team_id=team_id,
            user_id=user.telegram_id
        )

        await team_dao.update(filters=IdModel(id=existing_team.id), values=team)

        await invalidate_team_cache(redis=redis, team_id=existing_team.id, hackathon_id=existing_team.hackathon_id)
        await invalidate_user_cache(redis=redis, tg_id=user.telegram_id, invalidate_teams=True)

        return SuccessResponse(message="Команда успешно обновлена")

    except Exception as e:
        logger.error(f"Ошибка при обновлении команды: {e}")
        raise


@router.delete(
    path="/{team_id}",
    summary="Удалить команду по ID (только лидером)",
    response_model=Union[SuccessResponse, ErrorResponse],
    responses={
        200: generate_response_model(description="Успешный запрос. Возвращает сообщение об успешном удалении команды",
                                     model=SuccessResponse),
        401: generate_response_model("Ошибка авторизации"),
        403: generate_response_model("Пользователь не является лидером данной команды"),
        404: generate_response_model("Не найден пользователь или команда"),
        422: generate_response_model("Ошибка валидации входных данных"),
        500: generate_response_model()
    }
)
@exception_handler
async def delete_team(
        team_id: int,
        session: AsyncSession = Depends(db.get_db_with_commit),
        redis: CustomRedis = Depends(get_redis),
        user: SUser = Depends(fast_auth_user)
) -> SuccessResponse:
    """Удаляет команду и очищает кэш."""

    try:

        team_dao = TeamDAO(session)

        existing_team = await get_team_if_user_is_leader(
            redis=redis,
            session=session,
            team_id=team_id,
            user_id=user.telegram_id
        )

        await team_dao.delete(filters=IdModel(id=existing_team.id))

        await invalidate_team_cache(redis=redis, team_id=existing_team.id, hackathon_id=existing_team.hackathon_id)
        await invalidate_user_cache(redis=redis, tg_id=user.telegram_id, invalidate_teams=True)

        await invalidate_member_cache(
            redis=redis,
            team_id=existing_team.id,
            hackathon_id=existing_team.hackathon_id,
            tg_id=user.telegram_id,
            invalidate_leader=True
        )

        return SuccessResponse(message="Команда успешно удалена")

    except Exception as e:
        logger.error(f"Ошибка при удалении команды: {e}")
        raise


@router.get(
    path="/{team_id}/leader",
    summary="Проверить, является ли пользователь лидером команды",
    response_model=Union[SUserIsLeader, ErrorResponse],
    responses={
        200: generate_response_model(
            description="Успешный запрос. Возвращает информацию о том, является ли пользователь лидером команды",
            model=SUserIsLeader),
        401: generate_response_model("Ошибка авторизации"),
        404: generate_response_model("Не найден пользователь или команда"),
        500: generate_response_model()
    }
)
@exception_handler
async def check_user_is_leader(
        team_id: int,
        session: AsyncSession = Depends(db.get_db),
        redis: CustomRedis = Depends(get_redis),
        user: SUser = Depends(fast_auth_user)
) -> SUserIsLeader:
    """Проверяет, является ли пользователь лидером команды"""

    try:
        leader = await get_member_data_by_team_id(redis=redis, session=session, team_id=team_id, role="leader")
        if not leader or leader.user_id != user.telegram_id:
            return SUserIsLeader(is_leader=False)
        else:
            return SUserIsLeader(is_leader=True)
    except Exception as e:
        logger.error(f"Ошибка при проверке пользователя на лидерство: {e}")
        raise


@router.post(
    path="/{team_id}/join",
    summary="Вступить команду по ID",
    response_model=Union[SuccessResponse, ErrorResponse],
    responses={
        200: generate_response_model(
            description="Успешный запрос. Возвращает сообщение об успешном вступлении в команду",
            model=SuccessResponse),
        400: generate_response_model("Команда переполнена, вступить нельзя"),
        401: generate_response_model("Ошибка авторизации"),
        403: generate_response_model("Команда закрытого типа, вход разрешен только по приглашениям"),
        404: generate_response_model(
            "Пользователь не найден или не зарегистрирован или не найдена команда или участник"),
        409: generate_response_model("Участник уже участвует в хакатоне с другой командой"),
        422: generate_response_model("Ошибка валидации входных данных"),
        500: generate_response_model()
    }
)
@exception_handler
async def join_to_team(
        team_id: int,
        session: AsyncSession = Depends(db.get_db_with_commit),
        redis: CustomRedis = Depends(get_redis),
        user: SUser = Depends(fast_auth_user)
) -> SuccessResponse:
    try:

        is_register = check_registration_for_app(user=user)
        if not is_register:
            raise UserNotRegisteredToApp

        current_team = await get_team_data(redis=redis, session=session, team_id=team_id)
        if not current_team:
            raise TeamNotFoundException

        if not current_team.is_open:
            raise TeamCloseException

        existing_member = await find_existing_member_by_hackathon(
            redis=redis,
            session=session,
            user_id=user.telegram_id,
            hackathon_id=current_team.hackathon_id
        )
        if existing_member:
            raise MemberInTeamException

        current_hackathon = await get_hackathon_data(
            redis=redis,
            session=session,
            hackathon_id=current_team.hackathon_id
        )
        members_count = await count_members_in_team(redis=redis, session=session, team_id=current_team.id)

        if 0 < members_count >= current_hackathon.max_members:
            raise MaxTeamMembersExceededException

        new_member = await MemberDAO(session).add(values=MemberCreate(
            user_id=user.telegram_id,
            team_id=current_team.id,
            tg_name=user.username,
            role="member"
        ))

        await invalidate_member_cache(
            redis=redis,
            hackathon_id=current_team.hackathon_id,
            team_id=current_team.id,
            tg_id=user.telegram_id,
            member=SMember(**new_member.to_dict())
        )

        await invalidate_user_cache(redis=redis, tg_id=user.telegram_id)

        return SuccessResponse(message="Вы успешно присоединились к команде")

    except Exception as e:
        logger.error(f"Ошибка при вступлении в команду: {e}")
        raise


@router.post(
    path="/{team_id}/leave",
    summary="Покинуть команду по ID",
    response_model=Union[SuccessResponse, ErrorResponse],
    responses={
        200: generate_response_model(
            description="Успешный запрос. Возвращает сообщение об успешном выходе из команды",
            model=SuccessResponse),
        401: generate_response_model("Ошибка авторизации"),
        404: generate_response_model("Не найден пользователь, команда или участник"),
        422: generate_response_model("Ошибка валидации входных данных"),
        500: generate_response_model()
    }
)
@exception_handler
async def leave_from_team(
        team_id: int,
        session: AsyncSession = Depends(db.get_db_with_commit),
        redis: CustomRedis = Depends(get_redis),
        user: SUser = Depends(fast_auth_user)
) -> SuccessResponse:
    """Пользователь покидает команду и очищается кэш."""
    try:

        current_team = await get_team_data(redis=redis, session=session, team_id=team_id)
        if not current_team:
            raise TeamNotFoundException

        hackathon_id = current_team.hackathon_id
        current_team_id = current_team.id
        tg_id = user.telegram_id

        existing_member = await get_member_data_by_team_id(redis=redis, session=session, team_id=current_team_id,
                                                           user_id=tg_id)
        if not existing_member:
            raise MemberNotFoundException

        await MemberDAO(session).delete(filters=IdModel(id=existing_member.id))

        message = f"Вы успешно покинули команду {current_team.name}"

        if existing_member.role == "leader":

            await TeamDAO(session).delete(filters=IdModel(id=current_team_id))

            await invalidate_team_cache(redis=redis, hackathon_id=hackathon_id, team_id=current_team_id)

            await invalidate_member_cache(
                redis=redis,
                hackathon_id=hackathon_id,
                team_id=current_team_id,
                invalidate_leader=True
            )

            message += " и удалили ее"

        else:

            await invalidate_member_cache(
                redis=redis,
                hackathon_id=hackathon_id,
                team_id=current_team_id,
                tg_id=tg_id,
                invalidate_member=True
            )

        await invalidate_user_cache(redis=redis, tg_id=user.telegram_id, invalidate_teams=True)

        return SuccessResponse(message=message)

    except Exception as e:
        logger.error(f"Ошибка при выходе из команды: {e}")
        raise


@router.post(
    path="/invite",
    summary="Пригласить пользователя в команду (только лидером)",
    response_model=Union[SuccessResponse, ErrorResponse],
    responses={
        200: generate_response_model(
            description="Успешный запрос. Возвращает сообщение об успешной отправке приглашения в команду",
            model=SuccessResponse),
        400: generate_response_model("Команда переполнена, пригласить нельзя"),
        401: generate_response_model("Ошибка авторизации"),
        403: generate_response_model("Пользователь не является лидером данной команды"),
        404: generate_response_model("Не найден пользователь или хакатон или же команда, участвующая в хакатоне"),
        409: generate_response_model("Приглашение уже существует"),
        422: generate_response_model("Ошибка валидации входных данных"),
        500: generate_response_model()
    }
)
@exception_handler
async def invite_user_to_team(
        invite: InviteCreate,
        session: AsyncSession = Depends(db.get_db_with_commit),
        redis: CustomRedis = Depends(get_redis),
        user: SUser = Depends(fast_auth_user)
) -> SuccessResponse:
    """Приглашает пользователя в команду (только лидером команды)
    Приглашение отправляется ботом в телеграм, если боту разрешено отправлять сообщения"""
    try:

        invite_user = await redis_user_data(tg_id=invite.invite_user_id)
        if not invite_user:
            raise UserNotFoundException

        existing_invites = await get_all_invites_user_data(
            redis=redis,
            session=session,
            invite_user_tg_id=invite.invite_user_id
        )

        if existing_invites:

            team_ids = [invite.team_id for invite in existing_invites]

            if invite.team_id in team_ids:
                raise InvitationAlreadyExistsException

        current_team = await get_team_if_user_is_leader(
            redis=redis, session=session,
            team_id=invite.team_id,
            user_id=user.telegram_id
        )

        current_hackathon = await get_hackathon_data(
            redis=redis,
            session=session,
            hackathon_id=current_team.hackathon_id
        )
        if not current_hackathon:
            raise HackathonNotFoundException

        members_count = await count_members_in_team(redis=redis, session=session, team_id=current_team.id)
        if 0 < members_count >= current_hackathon.max_members:
            raise MaxTeamMembersExceededException

        add_invite: Invite = await InviteDAO(session).add(values=invite)

        await invalidate_invite_cache(redis=redis, tg_id=user.telegram_id)

        await redis.set_value_with_ttl(key=f"invite:{add_invite.id}", value=json.dumps(add_invite.to_dict()))

        await send_invite_to_user(
            redis=redis,
            invite_id=add_invite.id,
            invite_user_tg_id=add_invite.invite_user_id,
            team=current_team
        )

        return SuccessResponse(message="Вы успешно пригласили пользователя в команду")

    except Exception as e:
        logger.error(f"Ошибка при приглашении пользователя в команду: {e}")
        raise
