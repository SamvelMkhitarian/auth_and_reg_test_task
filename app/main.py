from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.rate_limit import limiter

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Инициализация при старте."""
    settings = get_settings()
    configure_logging(settings.log_format)
    logger.info("app_start", log_format=settings.log_format)
    yield
    logger.info("app_stop")


def create_app() -> FastAPI:
    """Фабрика приложения (удобно для тестов)."""
    app = FastAPI(
        title="Auth API",
        version="1.0.0",
        lifespan=lifespan,
    )
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
    app.include_router(api_router)
    return app


app = create_app()
