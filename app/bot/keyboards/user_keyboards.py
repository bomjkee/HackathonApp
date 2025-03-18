from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.web_app_info import WebAppInfo
from config import admins, front_site_url


def main_keyboard(user_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🌐 Открыть приложение", web_app=WebAppInfo(url=f"{front_site_url}"))
    kb.button(text="📚 Информация", callback_data="info")
    kb.button(text="✉️ Мои приглашения", callback_data="invites")
    if user_id in admins:
        kb.button(text="🔑 Админ панель", callback_data="admin_panel")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def back_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🔙 Назад", callback_data="back_home")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def invite_keyboard(invite_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✔️ Принять приглашение", callback_data=f"accept_invite_{invite_id}")
    kb.button(text="❌ Отклонить приглашение", callback_data=f"reject_invite_{invite_id}")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


