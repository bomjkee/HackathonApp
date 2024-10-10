from aiogram import F, Router, types, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InputFile
import app.keyboards as kb


router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.reply(f'Добро пожаловать, {message.from_user.full_name}', reply_markup=kb.main)

@router.message(Command('info'))
async def cmd_info(message: Message):
    await message.answer(f"```py\nprint('Привет, мир!')\n```", parse_mode='HTML')


@router.message(F.text)
async def none(message: Message):
    await message.answer(f'{message.from_user.full_name}, это тебе не гпт, повтори попытку')
