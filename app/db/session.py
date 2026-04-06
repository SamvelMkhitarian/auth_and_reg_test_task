from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings
from app.db.asyncpg_connect import connect_args_for_database_url

_engine: AsyncEngine | None = None
AsyncSessionLocal: async_sessionmaker[AsyncSession] | None = None


def _ensure_engine() -> async_sessionmaker[AsyncSession]:
    """Создаёт engine и фабрику сессий при первом обращении."""
    global _engine, AsyncSessionLocal
    if AsyncSessionLocal is None:
        settings = get_settings()
        url = str(settings.database_url)
        _engine = create_async_engine(
            url,
            echo=False,
            pool_pre_ping=True,
            connect_args=connect_args_for_database_url(url),
        )
        AsyncSessionLocal = async_sessionmaker(
            _engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    assert AsyncSessionLocal is not None
    return AsyncSessionLocal


def get_engine() -> AsyncEngine:
    """Возвращает async engine (после первого вызова _ensure_engine)."""
    _ensure_engine()
    assert _engine is not None
    return _engine


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency: асинхронная сессия БД."""
    session_factory = _ensure_engine()
    async with session_factory() as session:
        yield session
