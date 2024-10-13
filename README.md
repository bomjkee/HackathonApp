# Telegram бот на Aiogram 3 + SQLAlchemy

Данный проект представляет собой Telegram бота с интеграцией MiniApp и использованием фреймворка **Aiogram 3**, **SQLAlchemy** для работы с базой данных.

Для логирования используется удобная библиотека loguru. Благодаря этому логи красиво подсвечиваются в консоли и фоном записываются в файл логов.

## Технологический стек

- **Telegram API**: Aiogram 3
- **ORM**: SQLAlchemy с aiosqlite
- **База данных**: SQLite

## Обзор архитектуры

Проект следует архитектуре, вдохновленной микросервисами и лучшими практиками FastAPI.

### Структура проекта

```
├── app/
│   ├── db/
│   │   ├── dao/
|   |   |   |── base.py
│   |   ├── migrations/
│   │   |   ├── versions/
│   │   |   ├── env.py
│   |   ├── database.py
|   |   ├── models.py
|   |   |── dao.py
│   ├── routers/
|   |── typization/
|   |── main.py
├── bot/
│   ├── handlers/
│   │   ├── admin_router.py
│   │   ├── user_router.py
│   ├── keyboards/
│   │   ├── admin_keyboards.py
│   │   ├── user_keyboards.py
│   ├── bot.py
│   ├── run.py
├── static/
|   |── css/
|   |   |── normalize.css
|   |── img/
|   |   |── arrow.png
|   |   |── background.jpg
|   |── index.html
├── .env
├── .gitignore
├── alembic.ini
├── config.py
├── log.txt
└── requirements.txt
```

### Переменные окружения

Создайте файл `.env` в корне проекта:

```env
BOT_TOKEN=your_bot_token_here
ADMIN_IDS=[12345,344334]
```

### Зависимости

```
aiogram==3.13.1
aiosqlite==0.20.0
alembic==1.13.3
loguru==0.7.2
pydantic-settings==2.5.2
SQLAlchemy==2.0.35
```

## Управление базой данных

### Конфигурация базовой модели

В проекте используется базовая модель SQLAlchemy с общими полями:

```python
class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now()
    )

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + 's'

    def to_dict(self) -> dict:
        # Метод для преобразования объекта в словарь
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
```

### Объекты доступа к данным (DAO)

Проект реализует базовый класс BaseDAO с общими операциями базы данных:

- `find_one_or_none_by_id` - поиск по ID
- `find_one_or_none` - поиск одной записи по фильтру
- `find_all` - поиск всех записей по фильтру
- `add` - добавление записи
- `add_many` - добавление нескольких записей
- `update` - обновление записей
- `delete` - удаление записей
- `count` - подсчет количества записей
- `paginate` - пагинация
- `find_by_ids` - поиск по нескольким ID
- `upsert` - создание или обновление записи
- `bulk_update` - массовое обновление

Сервис-специфичные DAO наследуются от BaseDAO:

```python
from bot.dao.base import BaseDAO
from bot.users.models import User

class UserDAO(BaseDAO):
    model = User
```

Пример использования:
```python
user_info = await UserDAO.find_one_or_none(telegram_id=user_id)

await UserDAO.add(
    telegram_id=user_id,
    username=message.from_user.username,
    first_name=message.from_user.first_name,
    last_name=message.from_user.last_name,
    referral_id=ref_id
)
```


