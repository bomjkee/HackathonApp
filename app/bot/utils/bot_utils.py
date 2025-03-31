import asyncio

from loguru import logger
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from aiogram.types import CallbackQuery, InlineKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.typization.responses import STeam
from app.redis.custom_redis import CustomRedis
from app.redis.redis_operations.team import get_member_data_by_team_id
from app.bot.keyboards.user_keyboards import main_keyboard, invite_keyboard, back_keyboard, delete_message_keyboard
from config import bot


async def send_message_to_leader(
        redis: CustomRedis,
        session: AsyncSession,
        team_id: int,
        message: str = "У вас изменения в команде"
) -> None:

    try:
        leader = await get_member_data_by_team_id(redis=redis, session=session, team_id=team_id, role="leader")
        if leader:
            await bot.send_message(chat_id=leader.user_id, text=message, reply_markup=delete_message_keyboard())

    except TelegramForbiddenError:
        logger.warning(f"Бот заблокирован пользователем. Невозможно отправить уведомление лидеру.")


async def send_invite_to_user(
        redis: CustomRedis,
        invite_id: int,
        invite_user_tg_id: int,
        team: STeam
) -> None:
    try:

        logger.info("Отправка приглашения в Telegram...")

        message = await bot.send_message(
            chat_id=invite_user_tg_id,
            text=f"Вам пришло приглашение в команду {team.name}\n\n"
                 f"Описание команды: {team.description or 'нет'}",
            reply_markup=invite_keyboard(invite_id=invite_id)
        )

        await redis.set_value_with_ttl(f"invite_message_process:{invite_id}", value=str(message.message_id))
        await asyncio.sleep(0.5)

        await bot.send_message(
            chat_id=invite_user_tg_id,
            text="Вы вернулись в главное меню",
            reply_markup=main_keyboard(user_id=invite_user_tg_id)
        )
        logger.info("Приглашение отправлено")

    except TelegramForbiddenError:
        logger.warning(
            f"Бот заблокирован пользователем {invite_user_tg_id}. Невозможно отправить приглашение.")


async def send_edit_message(call: CallbackQuery, message: str, keyboard: InlineKeyboardMarkup) -> None:

    try:
        logger.info(f"Отправка сообщения пользователю {call.from_user.username}")
        await call.message.edit_text(text=f"`{message}`", reply_markup=keyboard, parse_mode="Markdown")

    except TelegramBadRequest:
        logger.warning("Ошибка при отправке сообщения (спам или пустое сообщение).")
        await call.answer(message)


async def delete_message(call: CallbackQuery) -> None:

    try:
        logger.info("Удаляем сообщение")
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

    except Exception as e:
        logger.warning(f"Произошла ошибка при удалении сообщения: {e}")
        await call.answer()


async def clear_message_and_answer(call: CallbackQuery, message: str) -> None:

    try:
        await delete_message(call)
        await call.answer(message)

    except Exception as e:
        logger.warning(f"Произошла ошибка при замене сообщения: {e}")
        await call.answer(message)


def get_bot_description() -> str:
    description = ("MiniApp приложение для регистрации в хакатонах РТУ МИРЭА, "
                   "созданное на основе фреймворка FastAPI и библиотеки aiogram. "
                   "Для обработки данных используется Redis и PostgreSQL. "
                   "Клиентская часть написана на React.ts, axios, zod, sdk-react со сборкой на Vite")

    return description
