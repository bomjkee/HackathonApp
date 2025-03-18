import asyncio
import json
from typing import List
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.redis.custom_redis import CustomRedis
from app.api.typization.responses import SInvite
from app.db.dao import InviteDAO
from app.api.typization.schemas import IdModel, InviteFilter
from config import bot

async def get_all_invites_user_data(redis: CustomRedis, session: AsyncSession,
                                    invite_user_tg_id: int) -> List[SInvite] | None:
    try:
        invites_cache_key = f"invites:user:{invite_user_tg_id}"

        invites_data = await redis.get_cached_data(cache_key=invites_cache_key,
                                                   fetch_data_func=InviteDAO(session).find_all,
                                                   model=SInvite,
                                                   filters=InviteFilter(invite_user_id=invite_user_tg_id))

        if invites_data is None:
            logger.error(f"Приглашения не найдены.")
            return None

        return invites_data

    except Exception as e:
        logger.error(f"Ошибка при получении приглашений: {e}")
        return None


async def get_invite_data_by_id(redis: CustomRedis, session: AsyncSession, invite_id: int) -> SInvite | None:
    try:
        invite_cache_key = f"invite:{invite_id}"

        invite_data = await redis.get_cached_data(cache_key=invite_cache_key,
                                                  fetch_data_func=InviteDAO(session).find_one_or_none,
                                                  model=SInvite,
                                                  filters=IdModel(id=invite_id))
        if invite_data is None:
            logger.error(f"Приглашения не найдены.")
            return None

        return invite_data

    except Exception as e:
        logger.error(f"Ошибка при получении приглашений: {e}")
        return None


async def bot_cleanup_invites(user_id: int, redis: CustomRedis, session: AsyncSession) -> None:
    """
    Удаляет не подтвержденные/отклоненные приглашения из чата.
    """
    try:

        invites_data = await get_all_invites_user_data(redis=redis, session=session, invite_user_tg_id=user_id)

        if invites_data:
            for invite in invites_data:

                invite_message_cache = await redis.get_value(f"invite_message_process:{invite.id}")
                if invite_message_cache:

                    message_id = int(invite_message_cache)
                    try:
                        await bot.delete_message(chat_id=user_id, message_id=message_id)

                        await redis.delete_key(invite_message_cache)
                        logger.info(f"Удалено сообщение {message_id} с приглашением в команду")

                    except Exception as e:
                        logger.warning(f"Ошибка при удалении сообщения {message_id}: {e}")

                else:
                    logger.info("Сообщение уже было обработано удалено")

    except Exception as e:
        logger.error(f"Произошла ошибка при очищении приглашений: {e}")



async def invalidate_invite_cache(redis: CustomRedis, tg_id: int | None = None, invite_id: int | None = None) -> None:

    if tg_id:
        invites_key = f"invites:user:{tg_id}"
        await redis.delete_key(invites_key)

    if invite_id:
        invite_key = f"invite:{invite_id}"
        await redis.delete_key(invite_key)
