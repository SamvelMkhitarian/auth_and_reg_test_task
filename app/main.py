import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.infrastructure.config import app_settings
from app.infrastructure.persistence.database import create_engine, create_session_factory
from app.presentation.api.routers import auth_router, users_router
from app.rate_limit import limiter

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    engine = create_engine(app_settings)
    app.state.session_factory = create_session_factory(engine)
    app.state.engine = engine
    logger.info("%s started", app_settings.app_name)
    yield
    await engine.dispose()
    logger.info("%s stopped", app_settings.app_name)


def create_app() -> FastAPI:
    app = FastAPI(
        title=app_settings.app_name,
        version="1.0.0",
        lifespan=lifespan,
    )
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]
    app.add_middleware(SlowAPIMiddleware)
    app.include_router(auth_router, prefix=app_settings.api_prefix)
    app.include_router(users_router, prefix=app_settings.api_prefix)
    return app


app = create_app()
