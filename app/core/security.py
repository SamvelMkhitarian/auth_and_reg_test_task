from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

import bcrypt
import jwt

from app.core.config import Settings, get_settings


def hash_password(plain_password: str) -> str:
    """Возвращает bcrypt-хеш пароля (12 rounds)."""
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt(rounds=12))
    return hashed.decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Проверяет пароль против хеша."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        password_hash.encode("utf-8"),
    )


def create_access_token(
    subject_user_id: int,
    settings: Settings | None = None,
) -> str:
    """Создаёт access JWT (срок из настроек, по умолчанию 30 мин)."""
    s = settings or get_settings()
    now = datetime.now(tz=UTC)
    expire = now + timedelta(minutes=s.access_token_expire_minutes)
    payload: dict[str, Any] = {
        "sub": str(subject_user_id),
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "jti": str(uuid4()),
    }
    return jwt.encode(payload, s.secret_key, algorithm=s.jwt_algorithm)


def create_refresh_token(
    subject_user_id: int,
    settings: Settings | None = None,
) -> str:
    """Создаёт refresh JWT (срок из настроек, по умолчанию 7 дней)."""
    s = settings or get_settings()
    now = datetime.now(tz=UTC)
    expire = now + timedelta(days=s.refresh_token_expire_days)
    payload: dict[str, Any] = {
        "sub": str(subject_user_id),
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "jti": str(uuid4()),
    }
    return jwt.encode(payload, s.secret_key, algorithm=s.jwt_algorithm)


def decode_token(token: str, settings: Settings | None = None) -> dict[str, Any]:
    """Декодирует JWT (проверка подписи и exp)."""
    s = settings or get_settings()
    return jwt.decode(token, s.secret_key, algorithms=[s.jwt_algorithm])
