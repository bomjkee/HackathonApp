from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def admin_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🏆 Управлять хакатонами", callback_data="get_hackathons")
    kb.button(text="🎉 Создать хакатон", callback_data="create_hackathon")
    kb.button(text="🏠 На главную", callback_data="back_home")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def choice_hackathon_keyboard(hackathons) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for hackathon in hackathons:
        kb.button(text=f"{hackathon.name}", callback_data=f"hackathon_{hackathon.id}")
    kb.button(text="🔙 Назад", callback_data="admin_panel")
    kb.button(text="🏠 На главную", callback_data="back_home")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def manage_hackathon_keyboard(hackathon_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="👥 Получить отчет о хакатоне", callback_data=f"members_hackathon_{hackathon_id}")
    kb.button(text="🗑️ Удалить хакатон", callback_data=f"delete_hackathon_{hackathon_id}")
    kb.button(text="🔙 В админ панель", callback_data="admin_panel")
    kb.adjust(1, 2)
    return kb.as_markup(resize_keyboard=True)


def confirm_delete_hackathon_keyboard(hackathon_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Да, удалить", callback_data=f"confirm_delete_hackathon_{hackathon_id}")
    kb.button(text="❌ Отмена", callback_data=f"admin_panel")
    kb.adjust(1)
    return kb.as_markup()


def cancel_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="❌ Отмена", callback_data="cancel_admin")
    return kb.as_markup()