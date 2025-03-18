from loguru import logger

from app.redis.custom_redis import CustomRedis
from config import settings


class RedisClient:
    """Класс для управления подключением к Redis с поддержкой явного и автоматического управления."""

    def __init__(
        self,
        url: str,
        socket_timeout: int = 20,
    ):
        self.url = url
        self.socket_timeout = socket_timeout
        self._client: CustomRedis | None = None

    async def connect(self):
        """Создает и сохраняет подключение к Redis."""
        if self._client is None:
            try:
                self._client = CustomRedis.from_url(url=self.url, socket_timeout=self.socket_timeout)
                await self._client.ping()
                logger.info("Redis подключен успешно")
            except Exception as e:
                logger.error(f"Ошибка подключения к Redis: {e}")
                raise

    async def close(self):
        """Закрывает подключение к Redis."""
        if self._client:
            await self._client.close()
            self._client = None
            logger.info("Redis соединение закрыто")

    def get_client(self) -> CustomRedis:
        """Возвращает объект клиента Redis."""
        if self._client is None:
            raise RuntimeError("Redis клиент не инициализирован. Проверьте lifespan.")
        return self._client

    async def __aenter__(self):
        """Поддерживает асинхронный контекстный менеджер."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Автоматически закрывает подключение при выходе из контекста."""
        await self.close()


redis_client = RedisClient(url=settings.get_redis_url())

async def get_redis() -> CustomRedis:
    """Возвращает объект клиента Redis."""
    return redis_client.get_client()