import json
from pyexpat.errors import messages
from typing import Union, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.utils.auth_dep import fast_auth_user
from config import redis, logger, bot
from app.db.dao import TeamDAO, MemberDAO, HackathonDAO, InviteDAO, UserDAO
from app.api.utils.api_utils import exception_handler
from app.api.utils.redis_operations import convert_redis_data, get_hackathon_by_id_from_redis, get_team_by_id_from_redis
from app.db.session_maker import db
from app.bot.keyboards.user_keyboards import invite_keyboard
from app.api.typization.schemas import (IdModel, NameModel, TeamCreate,
                                        InviteCreate, MemberCreate,
                                        TeamUpdate, MemberFind)
from app.api.typization.responses import (STeam, SMember, SUser,
                                          ErrorResponse, STeamWithMembers,
                                          SInvite, SuccessResponse, SHackathonInfo)
from app.api.typization.exceptions import (TeamNotFoundException, TeamsNotFoundException,
                                           TeamNameAlreadyExistsException, ForbiddenException,
                                           MaxTeamMembersExceededException, InvitationAlreadyExistsException,
                                           MemberNotFoundException, TeamAlreadyExistsException, UserNotFoundException)

router = APIRouter(prefix="/teams", tags=["Работа с командами"])


@router.get("/", response_model=Union[List[STeam], ErrorResponse],
            responses={400: {"model": ErrorResponse}})
@exception_handler
async def get_all_teams(session: AsyncSession = Depends(db.get_db)) -> List[STeam]:
    """Получает информацию о командах"""
    cache_key = "all_teams"

    try:
        cached_teams = await redis.get(cache_key)

        if cached_teams:
            teams_data = json.loads(cached_teams)
            logger.info("Команды из Redis")
            teams = [STeam(**team_data) for team_data in teams_data]
            return teams
        else:
            teams = await TeamDAO.find_all(session=session)
            if not teams:
                raise TeamsNotFoundException

            teams_data = [team.to_dict() for team in teams]

            await redis.set(cache_key, json.dumps(teams_data))
            await redis.expire(cache_key, 3600)

            return teams

    except Exception as e:
        logger.error(f"Error interacting with Redis: {e}")
        raise


@router.get("/{team_id}", response_model=Union[STeamWithMembers, ErrorResponse],
            responses={400: {"model": ErrorResponse}})
@exception_handler
async def get_team_by_id(team_id: int, session: AsyncSession = Depends(db.get_db)) -> STeamWithMembers:
    """Получает информацию о команде с ее участниками."""

    team_cache_key = f"team:{team_id}"

    try:
        cached_team_data = await redis.get(team_cache_key)
        if cached_team_data:
            team_data = json.loads(cached_team_data)
            logger.info("Команда из Redis")

            team = STeam(**convert_redis_data(team_data["team"]))
            members = [SMember(**convert_redis_data(member)) for member in team_data["members"]]

            return STeamWithMembers(team=team, members=members)
        else:
            team_data = await TeamDAO.find_one_or_none(session=session, filters=IdModel(id=team_id))
            if team_data is None:
                raise TeamNotFoundException

            members_team = await MemberDAO.find_all_by_team_id(session=session, team_id=team_id)
            if members_team is None:
                members_team = []

            team = STeam(**team_data.to_dict())
            members = [SMember(**member.to_dict()) for member in members_team]
            team_with_members = STeamWithMembers(team=team, members=members)

            await redis.set(team_cache_key, json.dumps(
                {"team": team.model_dump(), "members": [member.model_dump() for member in members]}))
            await redis.expire(team_cache_key, 3600)  # TTL = 1 час

            return team_with_members

    except Exception as e:
        logger.error(f"Ошибка при получении информации о команде: {e}")
        raise


@router.post("/", response_model=Union[SuccessResponse, ErrorResponse],
             responses={400: {"model": ErrorResponse}})
@exception_handler
async def create_team(team: TeamCreate,
                      session: AsyncSession = Depends(db.get_db_with_commit),
                      user: SUser = Depends(fast_auth_user)) -> SuccessResponse:
    """Создает новую команду и очищает кэш списка команд."""

    try:
        existing_team = await TeamDAO.find_one_or_none(session=session, filters=NameModel(name=team.name))
        if existing_team:
            raise TeamNameAlreadyExistsException

        new_team = await TeamDAO.add(session=session, values=team)

        existing_member = await MemberDAO.find_existing_member(session=session,
                                                               user_id=user.get("id"),
                                                               hackathon_id=new_team.hackathon_id)
        if existing_member:
            raise TeamAlreadyExistsException

        await MemberDAO.add(session=session, values=MemberCreate(user_id=user.get("id"),
                                                                 tg_name=user.get("username"),
                                                                 team_id=new_team.id,
                                                                 role="leader"))
        team_list_cache_key = "all_teams"
        await redis.delete(team_list_cache_key)

        return SuccessResponse(message="Команда была успешно создана")

    except Exception as e:
        logger.error(f"Ошибка при создании команды: {e}")
        raise


@router.put("/{team_id}", response_model=Union[SuccessResponse, ErrorResponse],
            responses={400: {"model": ErrorResponse}})
@exception_handler
async def update_team(team_id: int, team: TeamUpdate,
                      session: AsyncSession = Depends(db.get_db_with_commit),
                      user: SUser = Depends(fast_auth_user)) -> SuccessResponse:
    """Обновляет информацию о команде и очищает кэш команды и списка команд."""

    try:
        existing_team = await get_team_by_id_from_redis(session=session, team_id=team_id)

        leader = await MemberDAO.find_one_or_none(session=session, filters=MemberFind(team_id=existing_team.id,
                                                                                      user_id=user.get("id"),
                                                                                      role="leader"))
        if not leader:
            raise ForbiddenException

        updated_team_count = await TeamDAO.update(session=session, filters=IdModel(id=existing_team.id), values=team)
        if updated_team_count != 1:
            raise TeamNotFoundException

        team_list_cache_key = f"all_teams"
        await redis.delete(team_list_cache_key)

        team_cache_key = f"team:{existing_team.id}"
        await redis.delete(team_cache_key)

        return SuccessResponse(message="Команда успешно обновлена")

    except Exception as e:
        logger.error(f"Ошибка при обновлении команды: {e}")
        raise


@router.delete("/{team_id}", response_model=Union[SuccessResponse, ErrorResponse],
               responses={400: {"model": ErrorResponse}})
@exception_handler
async def delete_team(team_id: int, session: AsyncSession = Depends(db.get_db_with_commit),
                      user: SUser = Depends(fast_auth_user)) -> SuccessResponse:
    """Удаляет команду и очищает кэш команды и списка команд."""

    try:
        existing_team = await get_team_by_id_from_redis(session=session, team_id=team_id)

        leader = await MemberDAO.find_one_or_none(session=session, filters=MemberFind(team_id=existing_team.id,
                                                                                      user_id=user.get("id"),
                                                                                      role="leader"))
        if not leader:
            raise ForbiddenException

        members = await MemberDAO.find_all_by_team_id(session=session, team_id=existing_team.id)
        if len(members) > 1:
            raise ForbiddenException
        await TeamDAO.delete(session=session, filters=IdModel(id=existing_team.id))

        team_list_cache_key = f"all_teams"
        await redis.delete(team_list_cache_key)

        team_cache_key = f"team:{existing_team.id}"
        await redis.delete(team_cache_key)

        return SuccessResponse(message="Команда успешно удалена")

    except Exception as e:
        logger.error(f"Ошибка при удалении команды: {e}")
        raise


@router.post("/invite", response_model=SuccessResponse,
             responses={400: {"model": ErrorResponse}})
@exception_handler
async def invite_user_to_team(invite: InviteCreate,
                              session: AsyncSession = Depends(db.get_db),
                              user: SUser = Depends(fast_auth_user)) -> SuccessResponse:
    """Приглашает пользователя в команду.(только лидер команды)"""
    try:
        existing_invite = await InviteDAO.find_one_or_none(session=session, filters=invite)
        if existing_invite:
            raise InvitationAlreadyExistsException

        team = await get_team_by_id_from_redis(session=session, team_id=invite.team_id)

        leader = await MemberDAO.find_one_or_none(session=session, filters=MemberFind(team_id=invite.team_id,
                                                                                      user_id=user.get("id"),
                                                                                      role="leader"))
        if not leader:
            raise ForbiddenException

        invite_user = await UserDAO.find_one_or_none(session=session, filters=IdModel(id=invite.invite_user_id))
        if not invite_user:
            raise UserNotFoundException

        hackathon = await get_hackathon_by_id_from_redis(session=session, hackathon_id=team.hackathon_id)

        members_count = await MemberDAO.count(session=session, filters=MemberFind(team_id=invite.team_id))

        if members_count >= hackathon.max_members:
            raise MaxTeamMembersExceededException

        add_invite = await InviteDAO.add(session=session, values=invite)
        new_invite = SInvite(**add_invite.to_dict())

        invite_key = f"invite:{add_invite.id}"
        await redis.set(invite_key, json.dumps(new_invite.model_dump()), ex=3600)

        await bot.send_message(chat_id=add_invite.invite_user_id,
                               text=f"Вам пришло приглашение в команду {team.name}",
                               reply_markup=invite_keyboard(invite_id=add_invite.id))

        return SuccessResponse(message="Вы успешно пригласили пользователя в команду")

    except Exception as e:
        logger.error(f"Ошибка при приглашении пользователя в команду: {e}")
        raise


@router.post("/{team_id}/join", response_model=SuccessResponse,
             responses={400: {"model": ErrorResponse}})
@exception_handler
async def join_to_team(team_id: int, session: AsyncSession = Depends(db.get_db_with_commit),
                       user: SUser = Depends(fast_auth_user)) -> SuccessResponse:
    try:
        current_team = await get_team_by_id_from_redis(session=session, team_id=team_id)

        team_cache_key = f"team:{current_team.id}"
        await redis.delete(team_cache_key)

        return SuccessResponse(message="Вы успешно присоединились к команде")
    except Exception as e:
        logger.error(f"Ошибка при выходе из команды: {e}")
        raise



@router.delete("/{team_id}/leave", response_model=SuccessResponse,
               responses={400: {"model": ErrorResponse}})
@exception_handler
async def leave_team(team_id: int, session: AsyncSession = Depends(db.get_db_with_commit),
                     user: SUser = Depends(fast_auth_user)) -> SuccessResponse:
    """Пользователь покидает команду."""
    try:
        current_team = await get_team_by_id_from_redis(session=session, team_id=team_id)

        member = await MemberDAO.find_one_or_none(session=session,
                                                  filters=MemberFind(team_id=current_team.id, user_id=user.get("id")))
        if not member:
            raise MemberNotFoundException

        message = "Вы успешно покинули команду"
        if member.role == "leader":
            message += " и удалили ее"
            await TeamDAO.delete(session=session, filters=IdModel(id=current_team.id))

        await MemberDAO.delete(session=session, filters=IdModel(id=member.id))

        team_cache_key = f"team:{current_team.id}"
        await redis.delete(team_cache_key)

        return SuccessResponse(message=message)

    except Exception as e:
        logger.error(f"Ошибка при выходе из команды: {e}")
        raise
