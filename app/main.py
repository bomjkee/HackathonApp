from loguru import logger

from fastapi import FastAPI, Request
from uvicorn_worker import UvicornWorker

from app.api.routers import home, hackathon, team
from app.api.utils.api_utils import exception_handler
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.db.database_middleware_aiogram import DatabaseMiddlewareWithoutCommit, DatabaseMiddlewareWithCommit
from fastapi.staticfiles import StaticFiles
from aiogram.types import Update

from config import dp, bot, settings, front_site_url
from app.bot.handlers import user, admin, invite
from app.bot.main import start_bot, stop_bot


class CustomUvicornWorker(UvicornWorker):
    CONFIG_KWARGS = {
        "proxy_headers": True,
        "forwarded_allow_ips": "*"
    }


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting bot setup...")

    dp.update.middleware.register(DatabaseMiddlewareWithoutCommit())
    dp.update.middleware.register(DatabaseMiddlewareWithCommit())

    dp.include_router(user.router)
    dp.include_router(invite.router)
    dp.include_router(admin.router)

    await start_bot()

    webhook_url = settings.get_webhook_url()
    await bot.set_webhook(
        url=webhook_url,
        allowed_updates=dp.resolve_used_update_types(),
        drop_pending_updates=True
    )
    logger.info(f"Webhook set to {webhook_url}")
    yield

    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Webhook deleted")
    await stop_bot()
    logger.info("Shutting down bot...")


app = FastAPI()

origins = [
    "http://localhost:5173",
    front_site_url
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(Exception, exception_handler)

app.mount('/static', StaticFiles(directory='app/static'), 'static')

# @app.post("/webhook")
# async def webhook(request: Request) -> None:
#     logger.info("Обработка обновления...")
#     update = Update.model_validate(await request.json(), context={"bot": bot})
#     await dp.feed_update(bot, update)
#     logger.info("Обновление обработано")

# Подключаем маршруты
app.include_router(home.router)
app.include_router(hackathon.router)
app.include_router(team.router)
