from fastapi import HTTPException
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError, MultipleResultsFound

from app.db.database import async_session_maker
from config import logger


class BaseDAO:
    model = None

    @classmethod
    async def find_all(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            records = result.scalars().all()
            if len(records) > 0:
                logger.info(f"Найдено {len(records)} записей {cls.model.__name__}")
                return records
            else:
                logger.info(f"Записей {cls.model.__name__} не найдено.")
                return None


    @classmethod
    async def find_all_as_json(cls, **filter_by):
        records = await cls.find_all(**filter_by)
        if records:
            return [record.to_dict() for record in records]
        else:
            return None


    @classmethod
    async def find_one_or_none_by_id(cls, id: int):
        # Найти запись по ID
        logger.info(f"Поиск {cls.model.__name__} с ID: {id}")
        async with async_session_maker() as session:
            try:
                query = select(cls.model).filter_by(id=id)
                result = await session.execute(query)
                record = result.scalar_one_or_none()
                if record:
                    logger.info(f"Запись с ID {id} найдена.")
                else:
                    logger.info(f"Запись с ID {id} не найдена.")
                return record
            except SQLAlchemyError as e:
                logger.error(f"Ошибка при поиске записи с ID {id}: {e}")
                raise


    @classmethod
    async def find_one_or_none(cls, **filter_by):
        # Найти одну запись по фильтрам
        logger.info(f"Поиск одной записи {cls.model.__name__} по фильтрам: {filter_by}")
        async with async_session_maker() as session:
            try:
                query = select(cls.model).filter_by(**filter_by)
                result = await session.execute(query)
                record = result.scalar_one_or_none()
                if record:
                    logger.info(f"Запись найдена по фильтрам: {filter_by}")
                else:
                    logger.info(f"Запись не найдена по фильтрам: {filter_by}")
                return record
            except MultipleResultsFound:
                logger.error(f"Найдено несколько записей по фильтрам {filter_by}")
                raise HTTPException(status_code=400, detail="Найдено несколько записей, когда ожидалась одна или ни одной.")
            except SQLAlchemyError as e:
                logger.error(f"Ошибка при поиске записи по фильтрам {filter_by}: {e}")
                raise e


    @classmethod
    async def add(cls, **values):
        # Добавить одну запись
        logger.info(f"Добавление записи {cls.model.__name__} с параметрами: {values}")
        async with async_session_maker() as session:
            async with session.begin():
                new_instance = cls.model(**values)
                session.add(new_instance)
                try:
                    await session.commit()
                    logger.info(f"Запись {cls.model.__name__} успешно добавлена.")
                except SQLAlchemyError as e:
                    await session.rollback()
                    logger.error(f"Ошибка при добавлении записи: {e}")
                    raise e
                return new_instance


    @classmethod
    async def delete(cls, **filter_by):
        # Удалить запись по фильтрам
        logger.info(f"Удаление записи {cls.model.__name__} по фильтрам: {filter_by}")
        async with async_session_maker() as session:
            async with session.begin():
                try:
                    query = select(cls.model).filter_by(**filter_by)
                    result = await session.execute(query)
                    record = result.scalar_one_or_none()
                    if record:
                        await session.delete(record)
                        await session.commit()
                        logger.info(f"Запись {cls.model.__name__} успешно удалена.")
                    else:
                        logger.info(f"Запись не найдена по фильтрам: {filter_by}")
                except SQLAlchemyError as e:
                    await session.rollback()
                    logger.error(f"Ошибка при удалении записи по фильтрам {filter_by}: {e}")
                    raise e
                return record
    