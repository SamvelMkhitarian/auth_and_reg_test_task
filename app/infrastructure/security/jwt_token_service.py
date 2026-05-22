from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

import jwt

from app.application.ports.security import ITokenService, TokenClaims
from app.infrastructure.config.settings import Settings, get_settings


class JwtTokenService(ITokenService):
    """JWT-адаптер ITokenService."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    def create_access_token(self, user_id: int) -> str:
        return self._encode(user_id, token_type="access", minutes=self._settings.access_token_expire_minutes)

    def create_refresh_token(self, user_id: int) -> str:
        return self._encode(
            user_id,
            token_type="refresh",
            days=self._settings.refresh_token_expire_days,
        )

    def decode(self, token: str) -> dict[str, Any]:
        return jwt.decode(
            token,
            self._settings.secret_key,
            algorithms=[self._settings.jwt_algorithm],
        )

    def parse_refresh_claims(self, token: str) -> TokenClaims:
        return self._parse_claims(token, expected_type="refresh")

    def parse_access_claims(self, token: str) -> TokenClaims:
        return self._parse_claims(token, expected_type="access")

    def _parse_claims(self, token: str, *, expected_type: str) -> TokenClaims:
        try:
            data = self.decode(token)
        except jwt.PyJWTError as exc:
            raise ValueError("Invalid token") from exc
        if data.get("type") != expected_type:
            raise ValueError("Invalid token type")
        sub = data.get("sub")
        if sub is None:
            raise ValueError("Missing subject")
        try:
            user_id = int(sub)
        except (TypeError, ValueError) as exc:
            raise ValueError("Invalid subject") from exc
        return TokenClaims(subject_user_id=user_id, token_type=expected_type)

    def _encode(
        self,
        user_id: int,
        *,
        token_type: str,
        minutes: int | None = None,
        days: int | None = None,
    ) -> str:
        now = datetime.now(tz=UTC)
        if minutes is not None:
            expire = now + timedelta(minutes=minutes)
        elif days is not None:
            expire = now + timedelta(days=days)
        else:
            raise ValueError("Either minutes or days must be set")
        payload: dict[str, Any] = {
            "sub": str(user_id),
            "type": token_type,
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
            "jti": str(uuid4()),
        }
        return jwt.encode(
            payload,
            self._settings.secret_key,
            algorithm=self._settings.jwt_algorithm,
        )
