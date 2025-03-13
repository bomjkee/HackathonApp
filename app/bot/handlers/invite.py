import json
from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.typization.exceptions import TeamNotFoundException, InvitationNotFoundException, \
    MaxTeamMembersExceededException, ForbiddenException, UserNotRegisteredForHackathon, HackathonNotFoundException
from app.api.typization.responses import SMember, SInvite, STeam, SHackathonInfo
from app.api.typization.schemas import TelegramIDModel, UserInfoFromBot, IdModel, InviteFilter, MemberFind
from app.api.utils.redis_operations import convert_redis_data, get_hackathon_by_id_from_redis, \
    get_team_by_id_from_redis, get_invite_by_id_from_redis
from app.bot.keyboards.user_keyboards import main_keyboard, back_keyboard, invite_keyboard
from app.db.dao import UserDAO, MemberDAO, TeamDAO, HackathonDAO, InviteDAO
from app.db.session_maker import db
from config import bot, redis, logger

router = Router()


@router.callback_query(F.data == "invites")
async def get_invites(call: CallbackQuery, session_without_commit: AsyncSession) -> None:
    user_id = call.from_user.id
    invites_data = await InviteDAO.find_all(session=session_without_commit, filters=InviteFilter(invite_user_id=user_id))
    if not invites_data:
        await call.message.edit_text("На данный момент нет приглашений в команду", reply_markup=main_keyboard(user_id=user_id))
        return

    for invite in invites_data:
        team = await get_team_by_id_from_redis(session=session_without_commit, team_id=invite.team_id)
        await call.message.answer(f"Приглашение в команду {team.name}\nОписание команды: {team.description}", reply_markup=invite_keyboard(invite_id=invite.id))
    await call.message.answer("Вы вернулись в главное меню", reply_markup=main_keyboard(user_id=user_id))


@router.callback_query(F.data.startswith("accept_invite_"))
async def accept_invite(call: CallbackQuery, session_with_commit: AsyncSession) -> None:
    try:
        _, __, invite_id = call.data.split("_")
        user_id = call.from_user.id

        invite = await get_invite_by_id_from_redis(session=session_with_commit, invite_id=int(invite_id))
        team = await get_team_by_id_from_redis(session=session_with_commit, team_id=invite.team_id)
        hackathon = await get_hackathon_by_id_from_redis(session=session_with_commit, hackathon_id=team.hackathon_id)

        members_count = await MemberDAO.count(session=session_with_commit, filters=MemberFind(team_id=team.id))

        if members_count >= hackathon.max_members:
            raise MaxTeamMembersExceededException

        await MemberDAO.add(session=session_with_commit,
                            values=MemberFind(user_id=user_id, team_id=team.id))

        await InviteDAO.delete(session=session_with_commit, filters=invite)

        invite_key = f"invite:{invite_id}"
        await redis.delete(invite_key)

        team_cache_key = f"team:{team.id}"
        await redis.delete(team_cache_key)

        await call.message.edit_text("Приглашение принято успешно")

        leader = await MemberDAO.find_one_or_none(session=session_with_commit, filters=MemberFind(team_id=team.id, user_id=user_id, role="leader"))
        if leader:
            leader_user = await UserDAO.find_one_or_none(session=session_with_commit, filters=IdModel(id=user_id))
            if leader_user:
                await bot.send_message(leader_user.telegram_id,
                                       f"Пользователь {call.from_user.full_name} (@{call.from_user.username}) принял приглашение в вашу команду!",
                                       reply_markup=main_keyboard(user_id=leader_user.telegram_id))

    except InvitationNotFoundException:
        await call.message.edit_text("Приглашение не найдено")
    except TeamNotFoundException:
        await call.message.edit_text("Команда не найдена")
    except UserNotRegisteredForHackathon:
        await call.message.edit_text("Вы не зарегистрированы на хакатон")
    except MaxTeamMembersExceededException:
        await call.message.edit_text("В команде достигнуто максимальное количество участников")
    except HackathonNotFoundException:
        await call.message.edit_text("Хакатон, в котором участвует команда, не найден")
    except Exception as e:
        logger.error(f"Ошибка при принятии приглашения в команду: {e}")
        await call.message.edit_text("Произошла ошибка при принятии приглашения")
    finally:
        await call.message.answer("Вы вернулись в главное меню", reply_markup=main_keyboard(user_id=call.from_user.id))



@router.callback_query(F.data.startswith("reject_invite_"))
async def reject_invite(call: CallbackQuery, session_with_commit: AsyncSession) -> None:
    try:
        _, __, invite_id = call.data.split("_")
        user_id = call.from_user.id

        invite = await get_invite_by_id_from_redis(session=session_with_commit, invite_id=int(invite_id))

        invite_key = f"invite:{invite_id}"
        await redis.delete(invite_key)

        await InviteDAO.delete(session=session_with_commit, filters=invite)

        await call.message.edit_text("Приглашение отклонено")

        leader = await MemberDAO.find_one_or_none(session=session_with_commit,
                                                  filters=SMember(team_id=invite.team_id, role="leader"))
        if leader:
            leader_user = await UserDAO.find_one_or_none(session=session_with_commit, filters=IdModel(id=leader.id))
            if leader_user:
                await bot.send_message(leader_user.telegram_id,
                                       f"Пользователь {call.from_user.full_name} (@{call.from_user.username}) принял приглашение в вашу команду!",
                                       reply_markup=main_keyboard(user_id=leader_user.telegram_id))

    except InvitationNotFoundException:
        await call.message.edit_text("Приглашение не найдено")
    except Exception as e:
        logger.error(f"Ошибка при отклонении приглашения в команду: {e}")
        await call.message.edit_text("Произошла ошибка при отклонении приглашения")
    finally:
        await call.message.answer("Вы вернулись в главное меню", reply_markup=main_keyboard(user_id=call.from_user.id))
