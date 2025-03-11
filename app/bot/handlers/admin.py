from aiogram import F, Router, types, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from app.bot.keyboards.admin_keyboards import admin_keyboard
from app.db.dao import UserDAO


router = Router()


@router.callback_query(F.data == 'admin_panel')
async def admin_panel(call: CallbackQuery):
    await call.message.edit_text('Вы в админ панели', reply_markup=admin_keyboard())

