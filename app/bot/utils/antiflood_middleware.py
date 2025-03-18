import datetime
from typing import Callable, Awaitable, Dict, Any
from venv import logger

from aiogram import BaseMiddleware
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.types import TelegramObject, Message, CallbackQuery
from redis.asyncio import Redis


class AntiFloodMiddleware(BaseMiddleware):
    """
    Middleware для защиты от флуда. Использует Redis для отслеживания активности пользователей.
    """

    def __init__(self, redis: Redis, flood_limit: int = 2):
        self.redis = redis
        self.flood_limit = flood_limit
        self.warning_message = "Пожалуйста, не флудите."


    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """
        Вызывается для каждого обновления.
        """
        try:
            if isinstance(event, (Message, CallbackQuery)):
                tg_id = event.from_user.id
                key = f"antiflood:{tg_id}"

                last_request_time = await self.redis.get(key)

                if last_request_time:
                    last_request_time = float(last_request_time)
                    time_since_last_request = datetime.datetime.now().timestamp() - last_request_time

                    if time_since_last_request < self.flood_limit:
                        logger.info(f"Флуд от пользователя {tg_id}.")
                        await self._send_flood_warning(event, tg_id)
                        return
                    else:
                        await self.redis.set(key, datetime.datetime.now().timestamp())
                        return await handler(event, data)

                else:
                    await self.redis.set(key, datetime.datetime.now().timestamp())
                    return await handler(event, data)

        except Exception as e:
            logger.error(f"Ошибка в AntiFloodMiddleware: {e}")
            raise


    async def _send_flood_warning(self, event: TelegramObject, tg_id: int):
        """
        Отправляет предупреждение пользователю о флуде.
        """
        try:
            if isinstance(event, Message):
                await event.reply(self.warning_message)
            elif isinstance(event, CallbackQuery):
                try:
                    await event.answer(self.warning_message)
                except TelegramBadRequest:
                    logger.warning(f"Предупреждение о флуде для tg_id {tg_id} не поместилось в alert. Отправляем обычным сообщением.")
                    await event.message.answer(self.warning_message)

        except TelegramForbiddenError:
            logger.warning(f"Бот заблокирован пользователем {tg_id}. Невозможно отправить предупреждение о флуде.")
        except Exception as e:
            logger.error(f"Ошибка при отправке предупреждения о флуде пользователю {tg_id}: {e}", exc_info=True)
            raise

