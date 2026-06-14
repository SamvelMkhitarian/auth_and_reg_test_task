"""Фикстуры pytest: in-memory SQLite, схема через metadata.create_all."""

from __future__ import annotations

import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["SECRET_KEY"] = "pytest-secret-key-exactly-32bytes!!"

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.infrastructure.config import get_settings
from app.infrastructure.persistence.database import create_session_factory
from app.infrastructure.persistence.models import Base
from app.main import create_app

get_settings.cache_clear()


@pytest.fixture
async def test_app() -> AsyncGenerator[FastAPI, Any]:
    engine = create_async_engine(os.environ["DATABASE_URL"], echo=False)
    session_factory = create_session_factory(engine)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    app = create_app()
    app.state.session_factory = session_factory
    app.state.engine = engine

    @asynccontextmanager
    async def test_lifespan(app: FastAPI):
        yield

    app.router.lifespan_context = test_lifespan
    yield app
    await engine.dispose()
    get_settings.cache_clear()


@pytest.fixture
async def client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, Any]:
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def db_session(test_app: FastAPI) -> AsyncGenerator[AsyncSession, Any]:
    async with test_app.state.session_factory() as session:
        yield session
