from contextlib import asynccontextmanager

from aiogram.exceptions import TelegramBadRequest
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from aiogram.types import Update
from uvicorn_worker import UvicornWorker

from app.redis.redis_client import redis_client
from app.api.routers import home, hackathon, team
from app.api.utils.api_utils import exception_handler
from app.bot.main import start_bot, stop_bot
from config import bot, logger, front_site_url, dp, settings


class CustomUvicornWorker(UvicornWorker):
    CONFIG_KWARGS = {
        "proxy_headers": True,
        "forwarded_allow_ips": "*"
    }


@asynccontextmanager
async def lifespan(app: FastAPI):

    await redis_client.connect()
    await start_bot()

    webhook_url = settings.get_webhook_url()
    await bot.set_webhook(
        url=webhook_url,
        allowed_updates=dp.resolve_used_update_types(),
        drop_pending_updates=True
    )
    logger.info(f"Установлен вебхук: {webhook_url}")
    yield

    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Вебхук удален")
    await stop_bot()
    await redis_client.close()


def create_app() -> FastAPI:

    app = FastAPI(lifespan=lifespan)

    origins = [
        "http://localhost:5173",
        front_site_url
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(Exception, exception_handler)

    app.include_router(home.router)
    app.include_router(hackathon.router)
    app.include_router(team.router)
    logger.info("Приложение собрано и готово к работе")
    return app


app = create_app()


@app.post("/webhook")
async def webhook(request: Request) -> None:
    """Устанавливает вебхук для получения обновлений от телеграма"""
    try:
        logger.info("Обработка обновления...")
        update = Update.model_validate(await request.json(), context={"bot": bot})
        await dp.feed_update(bot, update)
        logger.info("Обновление обработано")
    except TelegramBadRequest:
        raise

