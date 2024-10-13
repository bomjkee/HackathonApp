import asyncio
import os
from loguru import logger
from aiogram.types import BotCommand, BotCommandScopeDefault
from handlers.admin_router import admin_router
from config import bot, admins


async def set_commands():
    commands = [BotCommand(command='start', description='Старт'),
                BotCommand(command='info', description='Информация о данном приложении'),
                BotCommand(command='delete', description='Удалить свои данные')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def start_bot():
    await set_commands()
    try:
        for admin_id in admins:
            await bot.send_message(admin_id, text='Бот запущен.')
    except Exception as e:
        logger.error(e)
    logger.info("Бот успешно запущен.")


async def stop_bot():
    try:
        for admin_id in admins:
            await bot.send_message(admin_id, text='Бот остановлен.')
    except Exception as e:
        logger.error(e)
    logger.info("Бот остановлен.")