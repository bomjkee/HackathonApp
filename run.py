import asyncio
import logging
import json # work with json file

from aiogram import Bot, Dispatcher
from app.handlers import router

'''
with open('token.json', 'r') as file:
    config = json.load(file)
'''

config = json.load(open('token.json', 'r'))

bot = Bot(config["settings"]["token"])
dp = Dispatcher()


async def main():
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')

