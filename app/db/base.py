from typing import List, TypeVar, Generic, Type
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete, func
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import Base

T = TypeVar(name="T", bound=Base)


class BaseDAO(Generic[T]):
    """Абстрактный класс для работы с базой данных."""

    model: Type[T] = None

    def __init__(self, session: AsyncSession):
        self._session = session
        if self.model is None:
            raise ValueError("Модель должна быть указана в дочернем классе")


    async def find_one_or_none_by_id(self, data_id: int):
        try:
            query = select(self.model).filter_by(id=data_id)
            result = await self._session.execute(query)
            record = result.scalar_one_or_none()
            log_message = f"Запись {self.model.__name__} с ID {data_id} {'найдена' if record else 'не найдена'}."
            logger.info(log_message)
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записи с ID {data_id}: {e}")
            raise


    async def find_one_or_none(self, filters: BaseModel):
        filter_dict = filters.model_dump(exclude_unset=True)
        logger.info(f"Поиск одной записи {self.model.__name__} по фильтрам: {filter_dict}")

        try:
            query = select(self.model).filter_by(**filter_dict)
            result = await self._session.execute(query)
            record = result.scalar_one_or_none()
            log_message = f"Запись {'найдена' if record else 'не найдена'} по фильтрам: {filter_dict}"
            logger.info(log_message)
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записи по фильтрам {filter_dict}: {e}")
            raise


    async def find_all(self, filters: BaseModel | None = None):
        filter_dict = filters.model_dump(exclude_unset=True) if filters else {}
        logger.info(f"Поиск всех записей {self.model.__name__} по фильтрам: {filter_dict}")
        try:
            query = select(self.model).filter_by(**filter_dict)
            result = await self._session.execute(query)
            records = result.scalars().all()
            logger.info(f"Найдено {len(records)} записей.")
            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске всех записей по фильтрам {filter_dict}: {e}")
            raise


    async def add(self, values: BaseModel):
        values_dict = values.model_dump(exclude_unset=True)
        logger.info(f"Добавление записи {self.model.__name__} с параметрами: {values_dict}")

        try:
            new_instance = self.model(**values_dict)
            self._session.add(new_instance)
            logger.info(f"Запись {self.model.__name__} успешно добавлена.")
            await self._session.flush()
            return new_instance
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при добавлении записи: {e}")
            raise


    async def add_many(self, instances: List[BaseModel]):
        values_list = [item.model_dump(exclude_unset=True) for item in instances]
        logger.info(f"Добавление нескольких записей {self.model.__name__}. "
                    f"Количество: {len(values_list)}")
        try:
            new_instances = [self.model(**values) for values in values_list]
            self._session.add_all(new_instances)
            logger.info(f"Успешно добавлено {len(new_instances)} записей.")
            await self._session.flush()
            return new_instances
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при добавлении нескольких записей: {e}")
            raise


    async def update(self, filters: BaseModel, values: BaseModel):
        filter_dict = filters.model_dump(exclude_unset=True)
        values_dict = values.model_dump(exclude_unset=True)
        logger.info(f"Обновление записей {self.model.__name__} "
                    f"по фильтру: {filter_dict} с параметрами: {values_dict}")
        try:
            query = (
                sqlalchemy_update(self.model)
                .where(*[getattr(self.model, k) == v for k, v in filter_dict.items()])
                .values(**values_dict)
                .execution_options(synchronize_session="fetch")
            )

            result = await self._session.execute(query)
            logger.info(f"Обновлено {result.rowcount} записей.")

            await self._session.flush()
            return result.rowcount
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при обновлении записей: {e}")
            raise


    async def delete(self, filters: BaseModel):
        filter_dict = filters.model_dump(exclude_unset=True)
        logger.info(f"Удаление записей {self.model.__name__} по фильтру: {filter_dict}")

        if not filter_dict:
            logger.error("Нужен хотя бы один фильтр для удаления.")
            raise ValueError("Нужен хотя бы один фильтр для удаления.")
        try:
            query = sqlalchemy_delete(self.model).filter_by(**filter_dict)
            result = await self._session.execute(query)

            logger.info(f"Удалено {result.rowcount} записей.")
            await self._session.flush()
            return result.rowcount
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при удалении записей: {e}")
            raise


    async def count(self, filters: BaseModel | None = None):
        filter_dict = filters.model_dump(exclude_unset=True) if filters else {}
        logger.info(f"Подсчет количества записей {self.model.__name__} по фильтру: {filter_dict}")

        try:
            query = select(func.count(self.model.id)).filter_by(**filter_dict)
            result = await self._session.execute(query)
            count = result.scalar()

            logger.info(f"Найдено {count} записей.")
            return count
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при подсчете записей: {e}")
            raise


    async def bulk_update(self, records: List[BaseModel]):
        logger.info(f"Массовое обновление записей {self.model.__name__}")

        try:
            updated_count = 0
            for record in records:
                record_dict = record.model_dump(exclude_unset=True)
                if "id" not in record_dict:
                    continue

                update_data = {k: v for k, v in record_dict.items() if k != "id"}
                stmt = (
                    sqlalchemy_update(self.model)
                    .filter_by(id=record_dict["id"])
                    .values(**update_data)
                )

                result = await self._session.execute(stmt)
                updated_count += result.rowcount

            logger.info(f"Обновлено {updated_count} записей")
            await self._session.flush()
            return updated_count
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при массовом обновлении: {e}")
            raise


    async def find_by_ids(self, ids: List[int]):
        """Найти несколько записей по списку ID"""
        logger.info(f"Поиск записей {self.model.__name__} по списку ID: {ids}")
        try:
            query = select(self.model).filter(self.model.id.in_(ids))
            result = await self._session.execute(query)

            records = result.scalars().all()
            logger.info(f"Найдено {len(records)} записей по списку ID.")
            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записей по списку ID: {e}")
            raise


    async def upsert(self, unique_fields: List[str], values: BaseModel):
        """Создать запись или обновить существующую"""
        values_dict = values.model_dump(exclude_unset=True)
        filter_dict = {field: values_dict[field] for field in unique_fields if field in values_dict}

        logger.info(f"Upsert для {self.model.__name__}")
        try:
            existing = await self.find_one_or_none(filters=BaseModel.model_construct(**filter_dict))
            if existing:
                # Обновляем существующую запись
                for key, value in values_dict.items():
                    setattr(existing, key, value)

                await self._session.flush()
                logger.info(f"Обновлена существующая запись {self.model.__name__}")
                return existing
            else:
                # Создаем новую запись
                new_instance = self.model(**values_dict)
                self._session.add(new_instance)

                await self._session.flush()
                logger.info(f"Создана новая запись {self.model.__name__}")
                return new_instance
        except SQLAlchemyError as e:
            await self._session.rollback()
            logger.error(f"Ошибка при upsert: {e}")
            raise
