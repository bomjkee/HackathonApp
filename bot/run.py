import asyncio
from handlers.user_router import user_router
from handlers.admin_router import admin_router
from bot import start_bot, stop_bot
from config import bot, dp


async def main():
    dp.include_router(user_router)
    dp.include_router(admin_router)
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())

        