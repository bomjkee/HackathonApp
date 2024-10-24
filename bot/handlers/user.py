from aiogram import F, Router, types, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from bot.keyboards.user_keyboards import main_keyboard, back_keyboard
from app.db.dao_models import UserDAO


router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    user_id = message.from_user.id
    is_user = await UserDAO.find_one_or_none(tg_id=user_id)
    if is_user:
        await message.answer(f'C возвращением, {message.from_user.full_name}', reply_markup=main_keyboard(message.from_user.id))
        return
    
    await UserDAO.add(
        tg_id=user_id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    await message.answer(f'Добро пожаловать, {message.from_user.full_name}', reply_markup=main_keyboard(message.from_user.id))


@router.message(Command('info'))
async def cmd_info(message: Message):
    
    bot_description = """
    This bot is designed to help users interact with our application.
    It provides various commands to get started and receive information.
    """
    
    await message.answer(f"Описание бота```{bot_description}```", parse_mode='Markdown', reply_markup=back_keyboard())


@router.callback_query(F.data == 'back_home')
async def go_back(query: CallbackQuery):
    await query.message.edit_text('Вы вернулись назад', reply_markup=main_keyboard(query.from_user.id))


@router.message(F.text)
async def none(message: Message):
    await message.answer(f'{message.from_user.full_name}, это тебе не гпт, повтори попытку')
