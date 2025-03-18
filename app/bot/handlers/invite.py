import asyncio
import json

from loguru import logger
from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.redis.custom_redis import CustomRedis
from app.redis.redis_client import redis_client
from app.redis.redis_operations.hackathon import get_hackathon_data
from app.redis.redis_operations.invite import get_all_invites_user_data, get_invite_data_by_id, \
    invalidate_invite_cache
from app.redis.redis_operations.member import find_existing_member_by_hackathon, count_members_in_team, \
    invalidate_member_cache
from app.redis.redis_operations.team import get_team_data
from app.redis.redis_operations.user import redis_user_data, invalidate_user_cache
from app.api.typization.bot_exceptions import TeamNotFoundException, InvitationNotFoundException, \
    MaxTeamMembersExceededException, HackathonNotFoundException, \
    MemberInTeamAlreadyExistsException, UserNotRegisteredForApp, UserNotFoundException
from app.api.typization.schemas import MemberCreate
from app.api.utils.api_utils import check_registration_for_app
from app.bot.keyboards.user_keyboards import main_keyboard, invite_keyboard
from app.bot.utils.bot_utils import send_message_to_leader, send_edit_message, delete_message, clear_message_and_answer
from app.db.dao import MemberDAO, InviteDAO

router = Router()


@router.callback_query(F.data == "invites")
async def get_invites(call: CallbackQuery, session_without_commit: AsyncSession) -> None:
    try:
        redis: CustomRedis = redis_client.get_client()

        invites_data = await get_all_invites_user_data(redis=redis,
                                                       session=session_without_commit,
                                                       invite_user_tg_id=call.from_user.id)

        if not invites_data:
            await send_edit_message(call=call, message="На данный момент нет приглашений в команду",
                                    keyboard=main_keyboard(user_id=call.from_user.id))
            return

        await delete_message(call=call)

        for invite in invites_data:

            team = await get_team_data(redis=redis, session=session_without_commit, team_id=invite.team_id)

            if team:
                message = await call.message.answer(f"Приглашение в команду {team.name}\nОписание команды: {team.description}",
                                          reply_markup=invite_keyboard(invite_id=invite.id))
                await redis.set_value_with_ttl(f"invite_message_process:{invite.id}", value=str(message.message_id))
                await asyncio.sleep(0.5)
        await call.message.answer("Вы вернулись в главное меню", reply_markup=main_keyboard(user_id=call.from_user.id))

    except Exception as e:
        logger.error(f"Ошибка при получении приглашений в команду: {e}")
        raise


@router.callback_query(F.data.startswith("accept_invite_"))
async def accept_invite(call: CallbackQuery, session_with_commit: AsyncSession) -> None:

    message = ""
    invite_id = int(call.data.split("_")[-1])
    user_id = call.from_user.id

    try:
        redis: CustomRedis = redis_client.get_client()

        invite = await get_invite_data_by_id(redis=redis, session=session_with_commit, invite_id=int(invite_id))
        if not invite:
            raise InvitationNotFoundException(invite_id=invite_id)

        existing_user = await redis_user_data(tg_id=user_id)
        if not existing_user:
            raise UserNotFoundException(user_id=user_id)

        is_registered = check_registration_for_app(existing_user)
        if not is_registered:
            raise UserNotRegisteredForApp(user_id=user_id)


        team = await get_team_data(redis=redis, session=session_with_commit, team_id=invite.team_id)
        if not team:
            raise TeamNotFoundException(team_id=invite.team_id)

        hackathon = await get_hackathon_data(redis=redis, session=session_with_commit, hackathon_id=team.hackathon_id)
        if not hackathon:
            raise HackathonNotFoundException(hackathon_id=team.hackathon_id)

        existing_member = await find_existing_member_by_hackathon(
            redis=redis,
            session=session_with_commit,
            hackathon_id=hackathon.id,
            user_id=user_id
        )
        if existing_member:
            raise MemberInTeamAlreadyExistsException()


        members_count = await count_members_in_team(redis=redis, session=session_with_commit, team_id=team.id)
        if 0 < members_count >= hackathon.max_members:
            raise MaxTeamMembersExceededException(team_id=team.id, max_members=hackathon.max_members)

        new_member = await MemberDAO(session_with_commit).add(values=MemberCreate(
            user_id=existing_user.telegram_id,
            team_id=team.id,
            tg_name=call.from_user.username,
            role="member"
        ))

        await InviteDAO(session_with_commit).delete(filters=invite)

        await invalidate_member_cache(redis=redis, team_id=team.id, hackathon_id=hackathon.id, tg_id=user_id,
                                      member=new_member)
        await invalidate_invite_cache(redis=redis, tg_id=call.from_user.id, invite_id=invite.id)
        await invalidate_user_cache(redis=redis, tg_id=user_id, invalidate_teams=True)

        await send_message_to_leader(
            redis=redis,
            session=session_with_commit,
            team_id=team.id,
            message=f"Пользователь {call.from_user.full_name} "
                    f"(@{call.from_user.username}) принял приглашение в вашу команду!"
        )

        await redis.delete_key(key=f"invite_message_process:{invite.id}")

        message = f"Вы вступили в команду{team.name}"

    except InvitationNotFoundException:
        message = "Приглашение не найдено"

    except TeamNotFoundException:
        message = "Команда не найдена (возможно удалена)"

    except UserNotRegisteredForApp:
        message = "Вы не зарегистрированы в приложении, зарегистрируйтесь для принятия приглашения"

    except MemberInTeamAlreadyExistsException:
        message = "Вы уже состоите в команде, для принятия приглашения покиньте команду"

    except MaxTeamMembersExceededException:
        message = "В команде достигнуто максимальное количество участников"

    except HackathonNotFoundException:
        message = "Хакатон, в котором участвует команда, не найден"

    except Exception as e:
        logger.error(f"Ошибка при принятии приглашения в команду: {e}")
        message = "Произошла ошибка при принятии приглашения"

    finally:
        await clear_message_and_answer(call=call, message=message)


@router.callback_query(F.data.startswith("reject_invite_"))
async def reject_invite(call: CallbackQuery, session_with_commit: AsyncSession) -> None:

    message = "Приглашение отклонено"
    invite_id = int(call.data.split("_")[-1])

    try:
        redis: CustomRedis = redis_client.get_client()

        invite = await get_invite_data_by_id(redis=redis, session=session_with_commit, invite_id=int(invite_id))
        if not invite:
            raise InvitationNotFoundException

        await InviteDAO(session_with_commit).delete(filters=invite)

        await invalidate_invite_cache(redis=redis, tg_id=call.from_user.id, invite_id=invite_id)

        await send_message_to_leader(
            redis=redis,
            session=session_with_commit,
            team_id=invite.team_id,
            message=f"Пользователь {call.from_user.full_name} "
                    f"(@{call.from_user.username}) отклонил приглашение в вашу команду!"
        )

        await redis.delete_key(key=f"invite_message_process:{invite.id}")

    except InvitationNotFoundException:
        message = "Приглашение не найдено"

    except Exception as e:
        logger.error(f"Ошибка при отклонении приглашения в команду: {e}")
        message = "Произошла ошибка при отклонении приглашения"

    finally:
        await clear_message_and_answer(call=call, message=message)
