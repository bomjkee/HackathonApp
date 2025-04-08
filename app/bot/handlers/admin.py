import asyncio

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types.input_file import FSInputFile
from loguru import logger
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.redis.custom_redis import CustomRedis
from app.redis.redis_client import redis_client
from app.api.typization.bot_exceptions import HackathonsNotFoundException, HackathonNotFoundException
from app.redis.redis_operations.hackathon import get_all_hackathons_data, get_hackathon_data
from app.bot.keyboards.admin_keyboards import admin_keyboard, choice_hackathon_keyboard, manage_hackathon_keyboard
from app.bot.utils.bot_utils import send_edit_message
from app.redis.redis_operations.invite import bot_cleanup_invites
from app.db.dao import UserDAO
from app.bot.utils.pdf_utils import create_hackathon_report_pdf


router = Router()


@router.callback_query(F.data == 'admin_panel')
async def admin_panel(call: CallbackQuery, session_without_commit: AsyncSession):
    redis: CustomRedis = redis_client.get_client()
    await bot_cleanup_invites(redis=redis, user_id=call.from_user.id, session=session_without_commit)

    await send_edit_message(call=call, message='`Вы в админ панели`', keyboard=admin_keyboard())


@router.callback_query(F.data == 'get_hackathons')
async def get_hackathons(call: CallbackQuery, session_without_commit: AsyncSession):
    message = "Выберите хакатон"
    kb = admin_keyboard()

    try:
        redis: CustomRedis = redis_client.get_client()

        hackathons = await get_all_hackathons_data(redis=redis, session=session_without_commit)
        if hackathons:
            kb = choice_hackathon_keyboard(hackathons=hackathons)

    except HackathonsNotFoundException:
        message = "На данный момент нет хакатонов"

    except Exception as e:
        message = f"Ошибка при получении хакатонов: {e}"
        logger.error(message)
    finally:
        await send_edit_message(call=call, message=message, keyboard=kb)


@router.callback_query(F.data.startswith('hackathon_'))
async def get_hackathon_info(call: CallbackQuery, state: FSMContext, session_without_commit: AsyncSession):
    message = ""
    kb = admin_keyboard()

    try:
        redis: CustomRedis = redis_client.get_client()
        await state.clear()

        hackathon_id = int(call.data.split('_')[-1])


        hackathon = await get_hackathon_data(redis=redis, session=session_without_commit, hackathon_id=hackathon_id)
        if not hackathon:
            raise HackathonNotFoundException

        message = (f"Информация о хакатоне {hackathon.name}\n\n"
                   f"Описание: {hackathon.description}\n\n"
                   f"Максимальное количество участников в команде: {hackathon.max_members}")
        kb = manage_hackathon_keyboard(hackathon_id=hackathon_id)

    except HackathonNotFoundException:
        message = "Хакатон не найден"

    except Exception as e:
        message = f"Ошибка при получении информации о хакатоне: {e}"
        logger.error(message)
    finally:
        await send_edit_message(call=call, message=message, keyboard=kb)





@router.callback_query(F.data.startswith('members_hackathon_'))
async def get_hackathon_members(call: CallbackQuery, session_without_commit: AsyncSession):
    hackathon_id = int(call.data.split('_')[-1])

    try:
        redis: CustomRedis = redis_client.get_client()
        hackathon_id = int(call.data.split('_')[-1])

        hackathon = await get_hackathon_data(redis=redis, session=session_without_commit, hackathon_id=hackathon_id)
        if not hackathon:
            raise HackathonNotFoundException

        user_dao = UserDAO(session_without_commit)
        participants = await user_dao.get_hackathon_participants(hackathon_id=hackathon_id)

        if not participants:
            await send_edit_message(
                call=call,
                message="В этом хакатоне пока нет участников",
                keyboard=manage_hackathon_keyboard(hackathon_id=hackathon_id)
            )
            return

        start_date = datetime.fromtimestamp(hackathon.start_date).strftime('%d.%m.%Y')
        end_date = datetime.fromtimestamp(hackathon.end_date).strftime('%d.%m.%Y')

        pdf_path = create_hackathon_report_pdf(
            participants,
            hackathon.name,
            start_date,
            end_date
        )

        await call.message.delete()
        await call.answer(text="Создание PDF завершено. Отправляю файл...",)

        asyncio.sleep(1)

        await call.message.answer_document(
            document=FSInputFile(path=pdf_path),
            caption=f"Список участников хакатона: {hackathon.name}",
            reply_markup=manage_hackathon_keyboard(hackathon_id=hackathon_id)
        )

    except HackathonNotFoundException:
        await send_edit_message(
            call=call,
            message="Хакатон не найден",
            keyboard=admin_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка при создании PDF: {e}")
        await send_edit_message(
            call=call,
            message=f"Произошла ошибка при создании PDF: {e}",
            keyboard=manage_hackathon_keyboard(hackathon_id=hackathon_id)
        )


@router.callback_query(F.data == "cancel_admin")
async def cmd_cancel(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await send_edit_message(call=call, message="Вы в админ панели", keyboard=admin_keyboard())



