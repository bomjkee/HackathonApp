import os

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,  InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.web_app_info import WebAppInfo
from dotenv import load_dotenv


load_dotenv()
BASE_SITE = os.getenv('BASE_SITE')


main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Открыть приложение', web_app=WebAppInfo(url=BASE_SITE))]
])

goBack = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='В главное меню', callback_data='back')]
])

