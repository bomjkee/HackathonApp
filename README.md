# Шаблон Telegram бота на Aiogram 3 + SQLAlchemy

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
├── telegram-bot/
│   ├── migration/
│   │   ├── versions
│   │   ├── env.py
│   ├── dao/
│   │   ├── base.py
│   ├── users/
│   │   ├── dao.py
│   │   ├── keyboards.py
│   │   ├── models.py
│   │   └── router.py
│   │   ├── utils.py
│   └── config.py
│   ├── database.py
│   ├── main.py
├── data/
│   ├── db
├── alembic.ini
├── .env
└── requirements.txt
├── app/
│   ├── dao/
│   │   ├── base.py
│   ├── migration/
│   │   ├── versions
│   │   ├── env.py
|   ├── static/
|   |   |── css/
|   |   |   |── style.css
|   |   |── img
|   |   |── js
|   |   |   |── script.js
|   |   |── index.html
│   ├── users/
│   │   ├── dao.py
│   │   ├── keyboards.py
│   │   ├── models.py
│   │   └── router.py
│   │   ├── utils.py
│   └── config.py
│   ├── database.py
│   ├── log.txt
|   |── main.py
├── data/
│   ├── db.sqlite3
├── alembic.ini
├── .env
└── requirements.txt
```

### Компоненты мини-сервиса

Каждый мини-сервис имеет следующую структуру:

- **keyboards.py**: Клавиатуры Telegram
- **dao.py**: Объекты доступа к базе данных через SQLAlchemy
- **models.py**: Модели SQLAlchemy, специфичные для сервиса
- **utils.py**: Вспомогательные функции и утилиты
- **handlers.py**: Обработчики Aiogram для сервиса

## Конфигурация

### Переменные окружения

Создайте файл `.env` в корне проекта:

```env
BOT_TOKEN=your_bot_token_here
ADMIN_IDS=[12345,344334]
```

- `BOT_TOKEN`: Получите у [BotFather](https://t.me/BotFather)
- `ADMIN_IDS`: Список Telegram ID администраторов бота. Можно получить тут Получите у [IDBot Finder Pro](https://t.me/get_tg_ids_universeBOT)

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

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now()
    )

    @classmethod
    @property
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + 's'

    def to_dict(self) -> dict:
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


