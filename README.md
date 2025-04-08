# Hackathon MiniApp Backend

Бэкенд часть приложения для регистрации и управления хакатонами РТУ МИРЭА. Проект реализован с использованием FastAPI и aiogram.

## 🚀 Возможности

- Управление хакатонами (создание, редактирование, удаление)
- Регистрация и управление командами
- Система приглашений участников
- Кэширование данных с использованием Redis
- Административная панель в Telegram
- Интеграция с PostgreSQL для хранения данных

## 🛠 Технологический стек

- **Backend Framework**: FastAPI
- **Telegram Bot**: aiogram 3.x
- **База данных**: PostgreSQL
- **Кэширование**: Redis
- **Аутентификация**: Telegram 
- **Документация**: Swagger/OpenAPI
- **Логирование**: loguru
- **Тестирование**: pytest

## 📋 Требования

- Python 3.12+
- PostgreSQL 15+
- Redis 7+

## 🚀 Установка и запуск

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/HackathonMiniApp.git
cd HackathonMiniApp
```

2. Установите зависимости:
```bash
poetry install
```

3. Создайте файл `.env` в корневой директории и заполните его :
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/hackathon_db
REDIS_URL=redis://localhost:6379/0
BOT_TOKEN=your_telegram_bot_token
ADMIN_IDS=123456789,987654321  # ID администраторов через запятую
```

4. Примените миграции:
```bash
alembic upgrade head
```

5. Запустите приложение:
```bash
uvicorn app.main:app --reload
```

## 📚 Структура проекта

```
HackathonMiniApp/
├── app/
│   ├── api/              # API эндпоинты
│   ├── bot/             # Telegram бот
│   ├── db/              # Работа с базой данных
│   ├── redis/           # Redis операции
│   └── main.py          # Точка входа
├── migrations/          # Миграции базы данных
├── tests/              # Тесты
├── alembic.ini         # Конфигурация Alembic
├── pyproject.toml      # Зависимости проекта
└── README.md           # Документация
```

## 🔐 Аутентификация и авторизация

- Администраторы определяются по их Telegram ID
- Telegram init data для API аутентификации
- Роли пользователей: администратор, лидер команды, участник

## 📊 База данных

Основные сущности:
- Хакатоны
- Команды
- Пользователи
- Приглашения
- Уведомления

## 🔄 Redis кэширование

Используется для:
- Кэширования данных хакатонов
- Хранения временных данных приглашений
- Управления состоянием бота

## 📝 API документация

После запуска приложения документация доступна по адресу:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🧪 Тестирование

```bash
pytest tests/
```

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой фичи (`git checkout -b feature/amazing-feature`)
3. Закоммитьте изменения (`git commit -m 'Add some amazing feature'`)
4. Запушьте ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

MIT License - смотрите файл [LICENSE](LICENSE) для подробностей
