import jwt
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User, UserRole
from app.schemas.auth import TokenPairOut
from app.schemas.user import UserRegisterIn
from app.use_cases import user as user_service
from app.use_cases.audit import log_action


class EmailAlreadyRegisteredError(Exception):
    """Email уже занят."""


class InvalidCredentialsError(Exception):
    """Неверный email или пароль."""


class InvalidRefreshTokenError(Exception):
    """Невалидный или просроченный refresh token."""


async def register_user(session: AsyncSession, payload: UserRegisterIn) -> User:
    """Создаёт пользователя с ролью free_user."""
    email = payload.email.lower().strip()
    user = User(
        email=email,
        password_hash=hash_password(payload.password),
        role=UserRole.free_user,
        is_active=True,
    )
    session.add(user)
    try:
        await session.flush()
    except IntegrityError:
        await session.rollback()
        raise EmailAlreadyRegisteredError from None
    await session.refresh(user)
    await log_action(
        session,
        action="register",
        user_id=user.id,
        detail=f"email={email}",
    )
    return user


async def login_user(session: AsyncSession, email: str, password: str) -> TokenPairOut:
    """Проверяет учётные данные и возвращает пару токенов."""
    user = await user_service.get_user_by_email(session, email)
    if user is None or not user.is_active:
        raise InvalidCredentialsError
    if not verify_password(password, user.password_hash):
        raise InvalidCredentialsError
    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    await log_action(
        session,
        action="login",
        user_id=user.id,
        detail="success",
    )
    return TokenPairOut(access_token=access, refresh_token=refresh)


async def refresh_access_token(session: AsyncSession, refresh_token: str) -> TokenPairOut:
    """Выдаёт новую пару токенов по валидному refresh."""
    try:
        data = decode_token(refresh_token)
    except jwt.PyJWTError as exc:
        raise InvalidRefreshTokenError from exc
    if data.get("type") != "refresh":
        raise InvalidRefreshTokenError
    sub = data.get("sub")
    if sub is None:
        raise InvalidRefreshTokenError
    try:
        user_id = int(sub)
    except (TypeError, ValueError) as exc:
        raise InvalidRefreshTokenError from exc
    user = await user_service.get_user_by_id(session, user_id)
    if user is None or not user.is_active:
        raise InvalidRefreshTokenError
    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    return TokenPairOut(access_token=access, refresh_token=refresh)
