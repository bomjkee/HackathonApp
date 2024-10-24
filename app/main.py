from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.pages import pages_router
from app.routers import hackathon, user, auth, team


def create_app() -> FastAPI:
    app = FastAPI()

    app.mount('/static', StaticFiles(directory='app/static'), name='static')
    app.include_router(pages_router.router, tags=['Страницы'])
    app.include_router(auth.router)
    app.include_router(user.router)
    app.include_router(hackathon.router)

    return app

app = create_app()