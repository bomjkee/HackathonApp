from fastapi import FastAPI
from app.routers.user import router


def create_app() -> FastAPI:

    app = FastAPI(
        title="Hackathon App"
    )
    # Подключаем маршруты
    app.include_router(router, prefix='/users')
    
    return app