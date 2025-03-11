from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.typization.schemas import TelegramIDModel, UserInfoFromBot
from app.bot.keyboards.user_keyboards import main_keyboard, back_keyboard
from app.db.dao import UserDAO
from app.db.session_maker import db
from config import bot

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, session_with_commit: AsyncSession) -> None:

    user = await UserDAO.find_one_or_none(session=session_with_commit, filters=(TelegramIDModel(telegram_id=message.from_user.id)))

    if not user:
        profile_photos = await bot.get_user_profile_photos(message.from_user.id, limit=1)
        if profile_photos.total_count != 0:
            photo = profile_photos.photos[0][-1].file_id

            await UserDAO.add(session=session_with_commit, values=UserInfoFromBot(
                telegram_id=int(message.from_user.id),
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                photo_url=photo
            ))
        else:
            await UserDAO.add(session=session_with_commit, values=UserInfoFromBot(
                telegram_id=int(message.from_user.id),
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name
            ))
        await message.answer(f'Добро пожаловать, {message.from_user.full_name}',
                             reply_markup=main_keyboard(message.from_user.id))
    else:
        await message.answer(f'C возвращением, {message.from_user.full_name}',
                             reply_markup=main_keyboard(message.from_user.id))


@router.message(Command('info'))
async def cmd_info(message: Message):

    bot_description = """
    This bot is designed to help users interact with our application.
    It provides various commands to get started and receive information.
    """

    await message.answer(f"Описание бота```{bot_description}```", parse_mode='Markdown', reply_markup=back_keyboard())


@router.callback_query(F.data == 'info')
async def callback_info(call: CallbackQuery):
    await call.message.edit_text('Информация', reply_markup=back_keyboard())


@router.callback_query(F.data == 'back_home')
async def go_back(call: CallbackQuery):
    await call.message.edit_text('Вы вернулись назад', reply_markup=main_keyboard(call.from_user.id))


