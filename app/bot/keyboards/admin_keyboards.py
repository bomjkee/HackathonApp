from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def admin_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Управлять хакатонами", callback_data="get_hackathons")
    kb.button(text="🏠 На главную", callback_data="back_home")
    kb.adjust(1)
    return kb.as_markup()


def choice_hackathon_keyboard(hackathons) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for hackathon in hackathons:
        kb.button(text=f"{hackathon.name}", callback_data=f"hackathon_{hackathon.id}")
    kb.button(text="🔙 Назад", callback_data="admin_panel")
    kb.button(text="🏠 На главную", callback_data="back_home")
    kb.adjust(2)
    return kb.as_markup()


def manage_hackathon_keyboard(hackathon_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Посмотреть текущих участников хакатона", callback_data=f"members_hackathon_{hackathon_id}")
    kb.button(text="🔙 В админ панель", callback_data="admin_panel")
    kb.button(text="🏠 На главную", callback_data="back_home")
    kb.adjust(1)
    return kb.as_markup()
