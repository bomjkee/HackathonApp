from pyexpat.errors import messages

from aiogram import F, Router, types, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from keyboards.user_keyboards import main_keyboard, back_keyboard

user_router = Router()


@user_router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.reply(f'Добро пожаловать, {message.from_user.full_name}', reply_markup=main_keyboard(message.from_user.id))


@user_router.message(Command('info'))
async def cmd_info(message: Message):
    bot_description = """
    This bot is designed to help users interact with our application.
    It provides various commands to get started and receive information.
    """
    await message.answer(f"Описание бота```{bot_description}```", parse_mode='Markdown', reply_markup=back_keyboard())


@user_router.callback_query(F.data == 'back_home')
async def go_back(query: CallbackQuery):
    await query.message.edit_text('Вы вернулись назад', reply_markup=main_keyboard(query.from_user.id))


@user_router.message(F.text)
async def none(message: Message):
    await message.answer(f'{message.from_user.full_name}, это тебе не гпт, повтори попытку')
