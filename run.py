import asyncio

if __name__ == "__main__":
    # from bot.main import create_bot
    # asyncio.run(create_bot())
    import uvicorn
    uvicorn.run(app="app.main:create_app", reload=True)
