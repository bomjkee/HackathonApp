import json
from loguru import logger
from pydantic import BaseModel
from redis.asyncio import Redis
from typing import Any, Callable, Awaitable, Dict, Union, Type, TypeVar


T = TypeVar("T", bound=BaseModel)


class CustomRedis(Redis):
    """Расширенный класс Redis с дополнительными методами"""

    async def delete_key(self, key: str):
        """Удаляет ключ из Redis."""
        await self.delete(key)
        logger.info(f"Ключ {key} удален")


    async def delete_keys_by_prefix(self, prefix: str):
        """Удаляет ключи, начинающиеся с указанного префикса."""
        keys = await self.keys(prefix + '*')
        if keys:
            await self.delete(*keys)
            logger.info(f"Удалены ключи, начинающиеся с {prefix}")


    async def delete_all_keys(self):
        """Удаляет все ключи из текущей базы данных Redis."""
        await self.flushdb()
        logger.info("Удалены все ключи из текущей базы данных Redis")


    async def get_value(self, key: str):
        """Возвращает значение ключа из Redis."""
        value = await self.get(key)
        if value:
            return value
        else:
            logger.info(f"Ключ {key} не найден")
            return None


    async def set_value(self, key: str, value: str):
        """Устанавливает значение ключа в Redis."""
        await self.set(key, value)
        logger.info(f"Установлено значение ключа {key}")


    async def set_value_with_ttl(self, key: str, value: str, ttl: int = 3600):
        """Устанавливает значение ключа с временем жизни в Redis."""
        await self.setex(key, ttl, value)


    async def exists(self, key: str) -> bool:
        """Проверяет, существует ли ключ в Redis."""
        return await super().exists(key)


    async def get_keys(self, pattern: str = '*'):
        """Возвращает список ключей, соответствующих шаблону."""
        return await self.keys(pattern)


    async def get_cached_data(
        self,
        cache_key: str,
        fetch_data_func: Callable[..., Awaitable[Any]],
        model: Type[T],
        *args,
        ttl: int = 3600,
        **kwargs
    ) -> Any:
        """Получает данные из кэша Redis или из БД, если их нет в кэше."""
        cached_data = await (self.get(cache_key))

        if cached_data:
            logger.info(f"Данные получены из кэша для ключа: {cache_key}")
            try:
                logger.info(f"Загружаем данные из Redis")
                data = json.loads(cached_data)

                if isinstance(data, list):
                    return [model.model_validate(item) for item in data]
                else:
                    return model.model_validate(data)

            except (json.JSONDecodeError, ValueError, TypeError) as e:
                logger.error(f"Ошибка при десериализации данных из кэша: {e}")
                await self.delete_key(cache_key)

        logger.info(f"Данные не найдены в кэше для ключа: {cache_key}, получаем из базы данных")
        try:

            data = await fetch_data_func(*args, **kwargs)
            if data is None:
                logger.info("Данные не найдены в базе данных")
                return None

            if isinstance(data, list):
                processed_data = [
                    item.to_dict() if hasattr(item, 'to_dict') else item
                    for item in data
                ]
                models = [model(**item) for item in processed_data]
                await self.set_value_with_ttl(key=cache_key, ttl=ttl, value=json.dumps(processed_data))

                logger.info(f"Список данных сохранены в кэш для ключа: {cache_key} с TTL: {ttl} сек")
                return models

            else:
                processed_data = data.to_dict() if hasattr(data, 'to_dict') else data
                model_instance = model(**processed_data)
                await self.set_value_with_ttl(key=cache_key, ttl=ttl, value=json.dumps(processed_data))

                logger.info(f"Данные сохранены в кэш для ключа: {cache_key} с TTL: {ttl} сек")
                return model_instance


        except Exception as e:
            logger.error(f"Ошибка при получении данных из базы данных или создании Pydantic модели: {e}")
            return None


    @staticmethod
    def convert_redis_data(data: Dict[str, str]) -> Dict[str, Union[str, int, float]]:
        """
        Преобразует данные из Redis (все строки) в соответствующие типы Python
        (int, float, str), где это возможно.
        """
        converted_data = {}
        for key, value in data.items():
            if isinstance(key, bytes):
                key = key.decode()

            if isinstance(value, bytes):
                value = value.decode()

            try:
                converted_data[key] = int(value)
            except ValueError:
                try:
                    converted_data[key] = float(value)
                except ValueError:
                    converted_data[key] = value
        return converted_data

