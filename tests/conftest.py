"""Фикстуры pytest: in-memory SQLite, схема через metadata.create_all."""

from __future__ import annotations

import os
import sys
from collections.abc import AsyncGenerator
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

from app.db import session as session_module
from app.db.base import Base
from app.main import app

# До импорта приложения задаём окружение
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["SECRET_KEY"] = "pytest-secret-key-exactly-32bytes!!"
os.environ["LOG_FORMAT"] = "console"

if "app.core.config" in sys.modules:
    sys.modules["app.core.config"].get_settings.cache_clear()


@pytest.fixture(autouse=True)
async def _engine_and_schema() -> AsyncGenerator[None, None]:
    """На каждый тест — чистая БД в памяти."""

    engine = create_async_engine(
        os.environ["DATABASE_URL"],
        echo=False,
    )
    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    session_module._engine = engine
    session_module.AsyncSessionLocal = session_factory

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
    session_module._engine = None
    session_module.AsyncSessionLocal = None


@pytest.fixture
async def client(_engine_and_schema: None) -> AsyncGenerator[AsyncClient, Any]:
    """HTTP-клиент к ASGI-приложению."""

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
