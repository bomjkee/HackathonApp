from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from requests import session
from sqlalchemy.ext.asyncio import AsyncSession

from app.redis.custom_redis import CustomRedis
from app.redis.redis_client import redis_client
from app.redis.redis_operations.invite import bot_cleanup_invites
from app.redis.redis_operations.user import redis_user_data
from app.api.typization.schemas import UserInfoFromBot
from app.bot.keyboards.user_keyboards import main_keyboard, back_keyboard
from app.bot.utils.bot_utils import send_edit_message, get_bot_description
from app.db.dao import UserDAO
from config import bot, logger


router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, session_with_commit: AsyncSession) -> None:
    try:
        logger.info(f"Пользователь {message.from_user.username} нажал /start")
        user = await redis_user_data(tg_id=message.from_user.id)

        if not user:
            user_dao = UserDAO(session_with_commit)

            profile_photos = await bot.get_user_profile_photos(message.from_user.id, limit=1)
            if profile_photos.total_count != 0:
                photo = profile_photos.photos[0][-1].file_id

                await user_dao.add(values=UserInfoFromBot(
                    telegram_id=int(message.from_user.id),
                    username=message.from_user.username,
                    first_name=message.from_user.first_name,
                    last_name=message.from_user.last_name,
                    photo_url=photo
                ))
            else:
                await user_dao.add(values=UserInfoFromBot(
                    telegram_id=int(message.from_user.id),
                    username=message.from_user.username,
                    first_name=message.from_user.first_name,
                    last_name=message.from_user.last_name
                ))
            await message.answer(f'Добро пожаловать, {message.from_user.full_name}',
                                 reply_markup=main_keyboard(message.from_user.id))
        else:
            await message.answer(f'C возвращением, {message.from_user.full_name}',
                                 reply_markup=main_keyboard(message.from_user.id))
    except Exception as e:
        logger.error(f"Ошибка при регистрации пользователя {message.from_user.username}: {e}")
        raise



@router.message(Command('info'))
async def cmd_info(message: Message):

    logger.info(f"Пользователь {message.from_user.username} нажал /info")
    bot_description = get_bot_description()

    await message.answer(f"Описание бота```{bot_description}```", parse_mode='Markdown', reply_markup=back_keyboard())



@router.callback_query(F.data == 'info')
async def callback_info(call: CallbackQuery, session_without_commit: AsyncSession):
    logger.info(f"Пользователь {call.from_user.username} запросил информацию о боте")
    bot_description = get_bot_description()

    redis: CustomRedis = redis_client.get_client()
    await bot_cleanup_invites(redis=redis, user_id=call.from_user.id, session=session_without_commit)

    await send_edit_message(call=call, message=bot_description, keyboard=back_keyboard())



@router.callback_query(F.data == 'back_home')
async def go_back(call: CallbackQuery):
    logger.info(f"Пользователь {call.from_user.username} вернулся назад")
    await send_edit_message(call=call, message="Вы вернулись назад", keyboard=main_keyboard(user_id=call.from_user.id))



@router.message(F.photo)
async def photo_handler(message: Message):
    logger.info(f"Пользователь {message.from_user.username} отправил фото")
    await message.answer(f"Id фотографии: `{message.photo[-1].file_id}`", parse_mode='MarkdownV2',
                         reply_markup=back_keyboard())



@router.message(F.document)
async def document_handler(message: Message):
    logger.info(f"Пользователь {message.from_user.username} отправил документ")
    await message.answer(f"Id документа: `{message.document.file_id}`", parse_mode='MarkdownV2',
                         reply_markup=back_keyboard())



@router.message(F.text)
async def no_handler(message: Message):
    logger.info(f"Пользователь {message.from_user.username} отправил нераспознанный текст")
    await message.answer(f"{message.from_user.username}, ваше сообщение не распознано",
                         reply_markup=main_keyboard(message.from_user.id))




