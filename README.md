# Мини-API: регистрация и авторизация

FastAPI, слоистая архитектура (Domain → Application → Infrastructure → Presentation), async SQLAlchemy 2.0, PostgreSQL, JWT, bcrypt, Alembic, Docker Compose.

## Архитектура

```
app/
├── domain/              # Сущности и enum без внешних зависимостей
├── application/       # Сервисы, DTO, порты (Protocol), исключения
├── infrastructure/    # ORM, репозитории, JWT, bcrypt, конфиг, БД
├── presentation/      # FastAPI роутеры, HTTP-схемы, маппинг в ответы
├── composition/       # Composition root: сборка зависимостей
└── main.py
```

Зависимости направлены внутрь: Presentation → Application → Domain; Infrastructure реализует порты Application.

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

## Тесты

```bash
uv sync --dev
pytest tests/ -v
```

Тесты используют SQLite в памяти.

## CI (GitHub Actions)

Workflow `.github/workflows/ci.yml` на каждый push и pull request:

1. **Lint** — Ruff, Flake8, Mypy, Vulture (кэш зависимостей через `setup-uv@v8.1.0`).
2. **Tests** — запускается только если lint прошёл; `pytest` с SQLite in-memory.

## Слои в деталях

| Слой | Ответственность |
|------|-----------------|
| **Domain** | `User`, `UserRole` — чистая модель |
| **Application** | `AuthService`, `UserService`; порты `IUserRepository`, `ITokenService`, `IUnitOfWork` |
| **Infrastructure** | SQLAlchemy-репозитории, `JwtTokenService`, `BcryptPasswordHasher` |
| **Presentation** | Роутеры, Pydantic-схемы, маппинг domain → HTTP |
| **Composition** | `build_auth_service`, `build_unit_of_work` |

Таблица `audit_logs` заполняется при регистрации и входе.
