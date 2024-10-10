import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, BotCommandScopeDefault
from dotenv import load_dotenv
from users.handlers import router

load_dotenv()
TOKEN = os.getenv('TOKEN')
admins = [805550691]

bot = Bot(TOKEN)
dp = Dispatcher()


async def set_commands():
    commands = [BotCommand(command='start', description='Старт'),
                BotCommand(command='info', description='Информация о данном приложении'),
                BotCommand(command='delete', description='Удалить свои данные')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def start_bot():
    await set_commands()
    for admin_id in admins:
        try:
            await bot.send_message(admin_id, text=f'Бот запущен.')
        except Exception as e:
            logging.error(e)


async def stop_bot():
    try:
        for admin_id in admins:
            await bot.send_message(admin_id, text='Бот остановлен.')
    except Exception as e:
        logging.error(e)


async def main():
    dp.include_router(router)
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print('Bot stopped')