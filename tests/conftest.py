import json
import httpx
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport, Response

from app.redis.custom_redis import CustomRedis
from app.redis.redis_client import redis_client
from app.main import app
from config import settings, logger


async def make_request(client: AsyncClient, api_url: str, headers: dict | None = None, method: str = 'GET',
                       data: dict | None = None) -> Response:
    """
    Выполняет HTTP-запрос указанным методом к заданному API URL.
    """
    method = method.upper()

    url = f"api.hackathonmirea.ru"

    try:
        match method:
            case 'GET':
                response = await client.get(url=url, headers=headers)
            case 'POST':
                response = await client.post(url=url, headers=headers, json=data)
            case 'PUT':
                response = await client.put(url=url, headers=headers, json=data)
            case 'PATCH':
                response = await client.patch(url=url, headers=headers, json=data)
            case 'DELETE':
                response = await client.delete(url=url, headers=headers)
            case _:
                raise ValueError(f"Неизвестный HTTP method: {method}")

        logger.info(f"\n\nURL: {url}"
                    f"\nМетод: {method}"
                    f"\nСтатус: {response.status_code}"
                    f"\nТело ответа: {json.dumps(response.json(), indent=4, ensure_ascii=False)}")
        return response

    except httpx.RequestError as e:
        logger.error(f"Ошибка во время запроса: {e}")
        raise



@pytest_asyncio.fixture(scope="function")
async def async_client():
    try:
        await redis_client.connect()
        async with AsyncClient(
                base_url="http://testserver",
                transport=ASGITransport(app=app),
                follow_redirects=True,
                verify=False
        ) as client:
            yield client
    except Exception as e:
        logger.error(f"Ошибка при инициализации тестового приложения: {e}")
    finally:
        redis_client.close()


@pytest.fixture
def authorization_headers():
    # Init data из Telegram
    return {
        "authorization": f"tma {settings.TMA}"
    }


@pytest.mark.asyncio
async def test_clear_redis(async_client: AsyncClient):
    redis: CustomRedis = redis_client.get_client()
    await redis.delete_all_keys()







