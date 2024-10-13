from aiogram import F, Router, types, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
import app.users.keyboards as kb


router = Router()


@router.message(Command('start'))
async def cmd_start(message: Message):
    await message.reply(f'Добро пожаловать, {message.from_user.full_name}', reply_markup=kb.main)


@router.message(Command('info'))
async def cmd_info(message: Message):
    bot_description = """
    This bot is designed to help users interact with our application.
    It provides various commands to get started and receive information.
    """
    await message.answer(f"Описание бота```{bot_description}```", parse_mode='Markdown', reply_markup=kb.goBack)


@router.callback_query(F.data == 'back')
async def go_back(query: CallbackQuery):
    await query.message.edit_text('Вы вернулись назад', reply_markup=kb.main)


@router.message(F.text)
async def none(message: Message):
    await message.answer(f'{message.from_user.full_name}, это тебе не гпт, повтори попытку')
