import os
from typing import List
from redis.asyncio import Redis
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from pydantic_settings import BaseSettings, SettingsConfigDict
# from apscheduler.jobstores.redis import RedisJobStore
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger

class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMINS_ID: List[int]

    DB_URL: str

    BASE_SITE: str
    FRONT_SITE: str

    FORMAT_LOG: str
    LOG_ROTATION: str

    SECRET_KEY: str
    ALGORITHM: str

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_USER: str
    REDIS_PASSWORD: str
    REDIS_USER_PASSWORD: str
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    )

    def get_webhook_url(self) -> str:
        return f"{self.BASE_SITE}/webhook"

    def get_redis_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


settings = Settings()


bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
admins = settings.ADMINS_ID

front_site_url = settings.FRONT_SITE
base_site_url = settings.BASE_SITE
db_url = settings.DB_URL
redis = Redis.from_url(url=settings.get_redis_url(), socket_timeout=20)


# apscheduler = AsyncIOScheduler(
#     jobstores={'default': RedisJobStore(url=settings.STORE_URL)}
# )
log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log.txt")
logger.add(log_file_path, format=settings.FORMAT_LOG, level="INFO", rotation=settings.LOG_ROTATION)


