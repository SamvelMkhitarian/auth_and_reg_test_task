# Мини-API: регистрация и авторизация

FastAPI, слоистая архитектура (Domain → Application → Infrastructure → Presentation), async SQLAlchemy 2.0, PostgreSQL, JWT, bcrypt, Alembic, Docker Compose.

## Архитектура

```
app/
├── domain/              # entities, enums, exceptions
├── application/         # services, ports (Protocol)
├── infrastructure/      # config, ORM, repository, JWT, bcrypt
├── presentation/api/    # routers, schemas, dependencies
└── main.py
```

Зависимости направлены внутрь: Presentation → Application → Domain. Infrastructure реализует порты Application.

## Запуск через Docker (рекомендуется)

```bash
docker compose up --build
```

- API: http://127.0.0.1:8080
- Swagger: http://127.0.0.1:8080/docs

## Локальный запуск

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
uv sync --dev
cp .env.example .env
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
| GET | `/api/v1/users/` | Список пользователей (только admin) |

На `/api/v1/auth/login` — не более 5 запросов в минуту с одного IP.

## Качество кода

```bash
uv sync --dev

# Все линтеры и тайпчекеры одной командой
uv run poe lint

# Тесты
uv run poe test

# Lint + тесты (перед push)
uv run poe check
```

Инструменты: Ruff, Flake8, Mypy, Vulture.

## CI (GitHub Actions)

Workflow `.github/workflows/ci.yml` на каждый push и pull request:

1. **Lint** — `uv run poe lint` (Ruff, Flake8, Mypy, Vulture).
2. **Tests** — `uv run poe test` с SQLite in-memory.

## Слои

| Слой | Ответственность |
|------|-----------------|
| **Domain** | `User`, `UserRole`, доменные исключения |
| **Application** | `AuthService`, порты `UserRepositoryPort`, `TokenServicePort` |
| **Infrastructure** | `SqlAlchemyUserRepository`, JWT, bcrypt, конфиг |
| **Presentation** | FastAPI-роутеры, Pydantic-схемы, DI |

Таблица `audit_logs` заполняется при регистрации и входе.
