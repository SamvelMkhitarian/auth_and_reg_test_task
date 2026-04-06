# Мини-API: регистрация и авторизация

FastAPI, async SQLAlchemy 2.0, PostgreSQL, JWT (access + refresh), bcrypt, Alembic, Docker Compose.

## Запуск через Docker (рекомендуется)

На машине нужны только Docker и Docker Compose.

```bash
docker compose up --build
```

После старта приложение доступно на **8080** на вашем компьютере (внутри контейнера по-прежнему порт 8000):

- API: http://127.0.0.1:8080
- Swagger: http://127.0.0.1:8080/docs

Нужен именно порт 8000 на хосте: `APP_PORT=8000 docker compose up --build`. Любой другой свободный порт: `APP_PORT=3000 docker compose up --build`.

Контейнер `app` ждёт PostgreSQL, применяет `alembic upgrade head` и запускает Uvicorn.

Переменные окружения можно переопределить через файл `.env` (см. `.env.example`) или секцию `environment` в `docker-compose.yml`. Для продакшена обязательно задайте свой `SECRET_KEY` (не короче 16 символов, для HS256 лучше ≥ 32 байта).

## Локальный запуск (без Docker)

Нужны Python 3.11+, PostgreSQL с созданной БД.

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
uv sync --dev
cp .env.example .env
# Отредактируйте .env: DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/dbname
alembic upgrade head
uvicorn app.main:app --reload
```

## Эндпоинты

| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/api/v1/auth/register` | Регистрация (email, пароль) |
| POST | `/api/v1/auth/login` | Логин → access + refresh JWT |
| POST | `/api/v1/auth/refresh` | Новая пара токенов по refresh |
| GET | `/api/v1/users/me` | Профиль (Bearer access token) |
| PUT | `/api/v1/users/me` | Обновление `full_name`, `phone` |

На `/api/v1/auth/login` действует ограничение: не более 5 запросов в минуту с одного IP.

## Тесты

```bash
uv sync --dev
pytest tests/ -v
```

Тесты используют SQLite в памяти и не требуют запущенного PostgreSQL.

## Структура

- `app/api/v1/` — роутеры
- `app/services/` — бизнес-логика
- `app/models/` — ORM-модели
- `app/schemas/` — Pydantic v2 (входы/выходы)
- `alembic/versions/` — миграции (создание таблиц без `create_all()` в проде)

Дополнительно: таблица `audit_logs` с записями при успешной регистрации и входе.
