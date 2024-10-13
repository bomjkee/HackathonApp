import os

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,  InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.web_app_info import WebAppInfo
from app.comfig import site_url


main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Открыть приложение', web_app=WebAppInfo(url=site_url))]
])

goBack = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='В главное меню', callback_data='back')]
])

