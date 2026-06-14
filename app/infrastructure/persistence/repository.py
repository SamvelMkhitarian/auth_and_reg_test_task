from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

import bcrypt
import jwt
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports import PasswordHasherPort, TokenClaims, TokenServicePort
from app.domain.entities import User
from app.domain.exceptions import EmailAlreadyRegisteredError
from app.infrastructure.config import Settings, app_settings
from app.infrastructure.persistence.models import AuditLogModel, UserModel


class SqlAlchemyUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: int) -> User | None:
        model = await self._session.get(UserModel, user_id)
        return _to_entity(model) if model else None

    async def get_by_email(self, email: str) -> User | None:
        normalized = email.strip().lower()
        result = await self._session.execute(
            select(UserModel).where(UserModel.email == normalized)
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def add(self, user: User) -> User:
        model = _to_model(user)
        self._session.add(model)
        try:
            await self._session.flush()
        except IntegrityError as exc:
            await self._session.rollback()
            raise EmailAlreadyRegisteredError from exc
        await self._session.refresh(model)
        await self._session.commit()
        return _to_entity(model)

    async def update(self, user: User) -> User:
        if user.id is None:
            raise ValueError("User id is required for update")
        model = await self._session.get(UserModel, user.id)
        if model is None:
            raise ValueError(f"User {user.id} not found")
        model.full_name = user.full_name
        model.phone = user.phone
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def list_all(self) -> list[User]:
        result = await self._session.scalars(select(UserModel).order_by(UserModel.id))
        return [_to_entity(model) for model in result.all()]

    async def log_audit(
        self,
        *,
        action: str,
        user_id: int | None = None,
        detail: str | None = None,
    ) -> None:
        entry = AuditLogModel(user_id=user_id, action=action, detail=detail)
        self._session.add(entry)
        await self._session.commit()


class BcryptPasswordHasher(PasswordHasherPort):
    def hash(self, plain_password: str) -> str:
        hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt(rounds=12))
        return hashed.decode("utf-8")

    def verify(self, plain_password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )


class JwtTokenService(TokenServicePort):
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or app_settings

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


def _to_entity(model: UserModel) -> User:
    return User(
        id=model.id,
        email=model.email,
        password_hash=model.password_hash,
        full_name=model.full_name,
        phone=model.phone,
        role=model.role,
        is_active=model.is_active,
        created_at=model.created_at,
    )


def _to_model(entity: User) -> UserModel:
    model = UserModel(
        email=entity.email,
        password_hash=entity.password_hash,
        full_name=entity.full_name,
        phone=entity.phone,
        role=entity.role,
        is_active=entity.is_active,
    )
    if entity.id is not None:
        model.id = entity.id
    return model
