from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.web_app_info import WebAppInfo
from config import site_url, admins



def main_keyboard(user_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🌐 Открыть приложение", web_app=WebAppInfo(url=f"{site_url}"))
    kb.button(text="📚 Информация", callback_data="info")
    if user_id in admins:
        kb.button(text="🔑 Админ панель", callback_data="admin_panel")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def back_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🔙 Назад", callback_data="back_home")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

