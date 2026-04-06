from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Конфигурация сервиса."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = Field(
        ...,
        alias="DATABASE_URL",
        description="Async SQLAlchemy URL (postgresql+asyncpg://...)",
    )
    secret_key: str = Field(..., alias="SECRET_KEY", min_length=16)
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30,
        alias="ACCESS_TOKEN_EXPIRE_MINUTES",
        ge=1,
    )
    refresh_token_expire_days: int = Field(
        default=7,
        alias="REFRESH_TOKEN_EXPIRE_DAYS",
        ge=1,
    )
    log_format: str = Field(default="json", alias="LOG_FORMAT")


@lru_cache
def get_settings() -> Settings:
    """Возвращает закэшированный экземпляр настроек."""
    return Settings()
