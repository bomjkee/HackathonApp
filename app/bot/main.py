import asyncio
from loguru import logger
from aiogram.exceptions import TelegramRetryAfter
from aiogram.types import BotCommand, BotCommandScopeDefault, MenuButtonWebApp, WebAppInfo

from app.redis.redis_client import redis_client
from app.bot.utils.database_middleware import DatabaseMiddlewareWithoutCommit, DatabaseMiddlewareWithCommit
from app.bot.handlers import user, admin, invite
from app.bot.utils.antiflood_middleware import AntiFloodMiddleware
from config import bot, admins, front_site_url, dp


def setup_middleware():
    dp.update.middleware.register(DatabaseMiddlewareWithoutCommit())
    dp.update.middleware.register(DatabaseMiddlewareWithCommit())

    dp.callback_query.middleware.register(AntiFloodMiddleware(redis=redis_client.get_client(), flood_limit=1))
    dp.message.middleware.register(AntiFloodMiddleware(redis=redis_client.get_client()))


def include_routers():
    dp.include_router(user.router)
    dp.include_router(invite.router)
    dp.include_router(admin.router)


async def set_commands():
    commands = [BotCommand(command='start', description='Старт'),
                BotCommand(command='delete', description='Удалить свои данные')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def set_button():
    await bot.set_chat_menu_button(menu_button=MenuButtonWebApp(text="App", web_app=WebAppInfo(url=f"{front_site_url}")))


async def start_bot():
    """ Запуск бота """
    logger.info("Бот настраивается...")
    try:
        setup_middleware()
        include_routers()

        await set_commands()
        await set_button()

        logger.info("Бот успешно запущен.")
        for adm in admins:
            await bot.send_message(chat_id=adm, text="Бот успешно запущен.")
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
        for adm in admins:
            await bot.send_message(chat_id=adm, text="Бот успешно остановлен.")
    except Exception as e:
        logger.error(f"Ошибка при остановке бота: {e}")


