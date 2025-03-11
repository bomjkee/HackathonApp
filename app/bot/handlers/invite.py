import json
from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.typization.exceptions import TeamNotFoundException, InvitationNotFoundException, \
    MaxTeamMembersExceededException, ForbiddenException, UserNotRegisteredForHackathon
from app.api.typization.responses import SMember, SInvite
from app.api.typization.schemas import TelegramIDModel, UserInfoFromBot, IdModel, InviteFilter
from app.api.utils.redis_operations import convert_redis_data
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
        team = await TeamDAO.find_one_or_none_by_id(session=session_without_commit, data_id=invite.team_id)
        await call.message.answer(f"Приглашение в команду {team.name}\nОписание команды: {team.description}", reply_markup=invite_keyboard(invite_id=invite.id))
    await call.message.answer("Вы вернулись в главное меню", reply_markup=main_keyboard(user_id=user_id))


@router.callback_query(F.data.startswith("accept_invite_"))
async def accept_invite(call: CallbackQuery, session_with_commit: AsyncSession) -> None:
    try:
        _, __, invite_id = call.data.split("_")
        user_id = call.from_user.id

        invite_key = f"invite:{invite_id}"
        invite_data = await redis.get(invite_key)

        if invite_data:
            invite = json.loads(invite_data)
            invite = SInvite(**convert_redis_data(invite))
        else:
            invite = await InviteDAO.find_one_or_none(session=session_with_commit, filters=IdModel(id=invite_id))
            if not invite:
                raise InvitationNotFoundException
            invite = SInvite(**invite.to_dict())

        team_id = invite.team_id

        team = await TeamDAO.find_one_or_none(session=session_with_commit, filters=IdModel(id=team_id))
        if not team:
            raise TeamNotFoundException

        members_count = await MemberDAO.count(session=session_with_commit, filters=IdModel(id=team_id))
        hackathon = await HackathonDAO.find_one_or_none(session=session_with_commit,
                                                        filters=IdModel(id=team.hackathon_id))
        if members_count >= hackathon.max_members:
            raise MaxTeamMembersExceededException

        await MemberDAO.add(session=session_with_commit,
                            values=SMember(user_id=user_id, team_id=team_id, role="member"))
        await redis.delete(invite_key)

        team_cache_key = f"team:{team_id}"
        await redis.delete(team_cache_key)

        await InviteDAO.delete(session=session_with_commit, filters=invite)

        await call.message.edit_text("Приглашение принято успешно")

        leader = await MemberDAO.find_one_or_none(session=session_with_commit, filters=SMember(team_id=invite.team_id,
                                                                                               user_id=user_id,
                                                  role="leader"))
        if not leader:
            raise ForbiddenException
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

        invite_key = f"invite:{invite_id}:{user_id}"
        invite_data = await redis.get(invite_key)

        if invite_data:
            invite = json.loads(invite_data)
            invite = SInvite(**convert_redis_data(invite))
            await redis.delete(invite_key)
        else:
            invite_row = await InviteDAO.find_one_or_none(session=session_with_commit, filters=IdModel(id=invite_id))
            if not invite_row:
                raise InvitationNotFoundException
            invite = SInvite(**invite_row.to_dict())

        await InviteDAO.delete(session=session_with_commit, filters=invite)  # Pass object instead of schema

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
