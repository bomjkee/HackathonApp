import asyncio
from aiogram.types import BotCommand, BotCommandScopeDefault

from bot.handlers import user, admin
from config import bot, dp, logger, admins

async def set_commands():
    commands = [BotCommand(command='start', description='Старт'),
                BotCommand(command='delete', description='Удалить свои данные')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())

async def start_bot():
    try:
        dp.include_router(user.router)
        dp.include_router(admin.router)
        logger.info("Бот успешно запущен.")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, skip_updates=True, timeout=5)
        await set_commands() 
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        logger.info('Бот остановлен')
    
if __name__ == "__main__":
    asyncio.run(start_bot())