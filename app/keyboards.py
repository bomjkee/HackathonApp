from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,  InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.web_app_info import WebAppInfo

main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Открыть приложение', web_app=WebAppInfo(url='https://hackathonmirea.ru'))]
])


