from datetime import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.typization.bot_exceptions import HackathonNotFoundException
from app.api.typization.schemas import HackathonCreate, IdModel
from app.bot.keyboards.admin_keyboards import admin_keyboard, confirm_delete_hackathon_keyboard, cancel_keyboard
from app.bot.utils.bot_utils import send_edit_message
from app.db.dao import HackathonDAO
from app.redis.redis_client import redis_client
from app.redis.redis_operations.hackathon import invalidate_hackathon_cache

router = Router()


class HackathonStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_start_description = State()
    waiting_for_description = State()
    waiting_for_max_members = State()
    waiting_for_start_date = State()
    waiting_for_end_date = State()


@router.callback_query(F.data == "create_hackathon")
async def start_create_hackathon(call: CallbackQuery, state: FSMContext):
    await state.set_state(HackathonStates.waiting_for_name)
    await call.message.delete()

    await call.message.answer(text="Введите название хакатона:", reply_markup=cancel_keyboard())
    await call.answer()


@router.message(HackathonStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(HackathonStates.waiting_for_start_description)

    await message.answer("Введите вступительное описание хакатона", reply_markup=cancel_keyboard())


@router.message(HackathonStates.waiting_for_start_description)
async def process_start_description(message: Message, state: FSMContext):
    await state.update_data(start_description=message.text)
    await state.set_state(HackathonStates.waiting_for_description)
    await message.answer("Введите полное описание хакатона", reply_markup=cancel_keyboard())


@router.message(HackathonStates.waiting_for_description)
async def process_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(HackathonStates.waiting_for_max_members)
    await message.answer("Введите максимальное количество участников в команде", reply_markup=cancel_keyboard())


@router.message(HackathonStates.waiting_for_max_members)
async def process_max_members(message: Message, state: FSMContext):
    try:
        max_members = int(message.text)
        if max_members < 1:
            await message.answer("Количество участников должно быть больше 0. Попробуйте еще раз", reply_markup=cancel_keyboard())
            return
        await state.update_data(max_members=max_members)
        await state.set_state(HackathonStates.waiting_for_start_date)
        await message.answer("Введите дату начала хакатона в формате DD.MM.YYYY (или отправьте '-' для пропуска)", reply_markup=cancel_keyboard())
    except ValueError:
        await message.answer("Пожалуйста, введите число. Попробуйте еще раз", reply_markup=cancel_keyboard())


@router.message(HackathonStates.waiting_for_start_date)
async def process_start_date(message: Message, state: FSMContext):
    if message.text == "-":
        await state.update_data(start_date=None)
    else:
        try:
            start_date = datetime.strptime(message.text, "%d.%m.%Y")

            if start_date < datetime.now():
                await message.answer("Дата начала не может быть в прошлом. Введите корректную дату:")
                return

            await state.update_data(start_date=start_date)
        except ValueError:
            await message.answer("Неверный формат даты. Используйте формат DD.MM.YYYY или отправьте '-' для пропуска", reply_markup=cancel_keyboard())
            return

    await state.set_state(HackathonStates.waiting_for_end_date)
    await message.answer("Введите дату окончания хакатона в формате DD.MM.YYYY (или отправьте '-' для пропуска)", reply_markup=cancel_keyboard())


@router.message(HackathonStates.waiting_for_end_date)
async def process_end_date(message: Message, state: FSMContext, session_with_commit: AsyncSession):

    if message.text == "-":
        await state.update_data(end_date=None)
    else:

        try:
            end_date = datetime.strptime(message.text, "%d.%m.%Y")

            data = await state.get_data()
            start_date = data.get("start_date")

            if start_date is not None and end_date <= start_date:
                await message.answer("Дата окончания должна быть позже даты начала. Введите корректную дату:")
                return

            await state.update_data(end_date=end_date)

        except ValueError:
            await message.answer("Неверный формат даты. Используйте формат DD.MM.YYYY или отправьте '-' для пропуска", reply_markup=cancel_keyboard())
            return

    data = await state.get_data()
    try:
        hackathon_data = HackathonCreate(**data)
        new_hackathon = await HackathonDAO(session_with_commit).add(hackathon_data)
        await invalidate_hackathon_cache(redis_client.get_client())

        await message.answer(
            f"Хакатон '{new_hackathon.name}' успешно создан!",
            reply_markup=admin_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка при создании хакатона: {e}")
        await message.answer(
            f"Произошла ошибка при создании хакатона: {str(e)}",
            reply_markup=admin_keyboard()
        )
    finally:
        await state.clear()


@router.callback_query(F.data.startswith("delete_hackathon_"))
async def confirm_delete_hackathon(call: CallbackQuery):
    hackathon_id = int(call.data.split("_")[-1])
    await send_edit_message(
        call=call,
        message="Вы уверены, что хотите удалить этот хакатон? Это действие нельзя отменить.",
        keyboard=confirm_delete_hackathon_keyboard(hackathon_id)
    )


@router.callback_query(F.data.startswith("confirm_delete_hackathon_"))
async def delete_hackathon(call: CallbackQuery, session_with_commit: AsyncSession):
    hackathon_id = int(call.data.split("_")[-1])
    try:
        hackathon_dao = HackathonDAO(session_with_commit)
        hackathon = await hackathon_dao.find_one_or_none_by_id(hackathon_id)

        if not hackathon:
            raise HackathonNotFoundException(hackathon_id=hackathon_id)

        await hackathon_dao.delete(filters=IdModel(id=hackathon_id))
        await invalidate_hackathon_cache(redis_client.get_client(), hackathon_id=hackathon_id, invalidate_teams=True)

        await send_edit_message(
            call=call,
            message=f"Хакатон '{hackathon.name}' успешно удален!",
            keyboard=admin_keyboard()
        )
    except HackathonNotFoundException:
        await send_edit_message(
            call=call,
            message="Хакатон не найден",
            keyboard=admin_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка при удалении хакатона: {e}")
        await send_edit_message(
            call=call,
            message=f"Произошла ошибка при удалении хакатона: {str(e)}",
            keyboard=admin_keyboard()
        )


