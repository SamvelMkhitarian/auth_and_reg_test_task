from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.infrastructure.config import Settings, app_settings


def connect_args_for_database_url(database_url: str) -> dict:
    """Отключает SSL по умолчанию для asyncpg, если в URL это явно не настроено."""
    if not database_url.startswith("postgresql+asyncpg"):
        return {}
    if "ssl" in make_url(database_url).query:
        return {}
    return {"ssl": False}


def create_engine(settings: Settings | None = None) -> AsyncEngine:
    settings = settings or app_settings
    url = str(settings.database_url)
    return create_async_engine(
        url,
        echo=False,
        pool_pre_ping=True,
        connect_args=connect_args_for_database_url(url),
    )


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
