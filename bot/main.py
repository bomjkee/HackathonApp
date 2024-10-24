import asyncio

from config import bot, dp
from bot.bot import start_bot, stop_bot
from bot.handlers import user, admin


async def create_bot():
    dp.include_router(user.router)
    dp.include_router(admin.router)
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)
    try:
        await dp.start_polling(bot, skip_updates=True, timeout=5)
    finally:
        await bot.session.close()

