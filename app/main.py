from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from uvicorn_worker import UvicornWorker

from app.redis.redis_client import redis_client
from app.api.routers import home, hackathon, team
from app.api.utils.api_utils import exception_handler
from config import logger, front_site_url


class CustomUvicornWorker(UvicornWorker):
    CONFIG_KWARGS = {
        "proxy_headers": True,
        "forwarded_allow_ips": "*"
    }


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_client.connect()
    yield
    await redis_client.close()


def create_app() -> FastAPI:

    app = FastAPI(
        lifespan=lifespan,
        title="Hackathons Mirea API",
        description="Описание моего API для Telegram Mini App 'Хакатоны РТУ МИРЭА'",
        version="2.0",
        contact={
            "name": "bomjkee",
            "tg_bot": "@hackathons_mirea_bot"
        }
    )

    origins = [
        'http://localhost:5173',
        front_site_url
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=3600,
    )

    app.add_exception_handler(Exception, exception_handler)

    app.include_router(home.router)
    app.include_router(hackathon.router)
    app.include_router(team.router)

    logger.info("Приложение собрано и готово к работе")

    return app


app = create_app()
