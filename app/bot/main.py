import asyncio
from aiogram.exceptions import TelegramRetryAfter
from aiogram.types import BotCommand, BotCommandScopeDefault, MenuButtonWebApp, WebAppInfo
from config import bot, logger, admins, front_site_url


async def set_commands():
    commands = [BotCommand(command='start', description='Старт'),
                BotCommand(command='delete', description='Удалить свои данные')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def set_button():
    await bot.set_chat_menu_button(menu_button=MenuButtonWebApp(text="App", web_app=WebAppInfo(url=f"{front_site_url}")))


async def start_bot():
    try:
        logger.info("Бот успешно запущен.")
        await set_commands()
        await set_button()
        for admin in admins:
            await bot.send_message(chat_id=admin, text="Бот успешно запущен.")
    except TelegramRetryAfter as e:
        retry_after = e.retry_after
        logger.warning(f"Бот был заблокирован на {retry_after} секунд.")
        await asyncio.sleep(retry_after)
        await start_bot()
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")


async def stop_bot():
    try:
        logger.info("Бот успешно остановлен.")
        for admin in admins:
            await bot.send_message(chat_id=admin, text="Бот успешно остановлен.")
    except Exception as e:
        logger.error(f"Ошибка при остановке бота: {e}")


