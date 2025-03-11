import json
import httpx
from httpx import AsyncClient, ASGITransport

from app.main import app
from config import settings, logger, redis


async def test_request_func(api_url: str, headers: dict | None = None, method: str = 'GET', data: dict | None = None):
    """
    Выполняет HTTP-запрос указанным методом к заданному API URL.

    Аргументы:
        api_url: URL API-эндпоинта.
        headers: Словарь HTTP-заголовков для включения в запрос.
            По умолчанию None.
        method: HTTP-метод для использования (GET, POST, PUT, DELETE, PATCH).
            По умолчанию 'GET'. Регистр не учитывается.
        data: Словарь данных для отправки в теле запроса для POST, PUT
            и PATCH запросов. По умолчанию None.
    """
    method = method.upper()

    url = f"{settings.BASE_SITE}{api_url}"

    async with AsyncClient(
            base_url="http://testserver",
            headers=headers,
            transport=ASGITransport(app=app),
            follow_redirects=True,
            verify=False
    ) as client:
        try:
            match method:
                case 'GET':
                    response = await client.get(url=url, headers=headers)
                case 'POST':
                    response = await client.post(url=url, headers=headers, json=data)
                case 'PUT':
                    response = await client.put(url=url, headers=headers, json=data)
                case 'DELETE':
                    response = await client.delete(url=url, headers=headers)
                case _:
                    raise ValueError(f"Unsupported HTTP method: {method}")

            logger.info(f"\n\nURL: {url}"
                  f"\nМетод: {method}"
                  f"\nСтатус: {response.status_code}"
                  f"\nТело ответа: {json.dumps(response.json(), indent=4, ensure_ascii=False)}")
        except httpx.RequestError as e:
            logger.error(f"Ошибка во время запроса: {e}")
            return None



# Тестирование запросов к API
async def main():
    # Init data из Telegram
    front_headers = {
        "authorization": "tma query_id=AAFjugMwAAAAAGO6AzDtwMz4&user=%7B%22id%22%3A805550691%2C%22first_name%22%3A%22%E5%8C%9A%E3%84%A5%E3%84%96%E3%84%A9%E1%97%AA%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22bomjkee%22%2C%22language_code%22%3A%22ru%22%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Ft.me%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2FSIl_BF-VFBBmT7XImJOngWVlM5LUe2v0mWIrah8hnJw.svg%22%7D&auth_date=1741641618&signature=-rip8aot3_GFrrnSTC_Cbku1WPY6SBrZBIDA0xEFCh6neeqpHj_CaeUGmO5eOvUbWO8MDO5LwpJhIMuztBEsBw&hash=48e6354937fe36e402a611a1e4bee0750bd3ff3db1090be41c69fa0c0fe056e9"
    }

    # # GET запросы
    # # Получить хакатоны +
    # await test_request_func("/hackathons")
    # # Получить хакатон по ID +
    # await test_request_func("/hackathons/1")
    # # Получить команды +
    # await test_request_func("/teams")
    # # Получить команду по ID +
    # await test_request_func("/teams/1")
    # # Просмотр профиля и команды +
    # await test_request_func("/my_profile", headers=front_headers)
    # # Проверка регистрации в приложении
    # await test_request_func("register", headers=front_headers)


    # POST запросы
    # Создание команды
    team_create = {"name": "Olso",
                   "is_open": True,
                   "description": "Команда разработчиков корпоративных приложений",
                   "hackathon_id": 1}
    await test_request_func("/teams", method="POST", headers=front_headers, data=team_create)


    # PUT запросы

    # DELETE запросы
    await test_request_func("/teams/10", method="DELETE", headers=front_headers)

if "__main__" == __name__:
    import asyncio
    asyncio.run(main())



