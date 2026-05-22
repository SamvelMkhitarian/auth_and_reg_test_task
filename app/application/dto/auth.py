from dataclasses import dataclass


@dataclass(frozen=True)
class RegisterUserCommand:
    """Команда регистрации."""

    email: str
    password: str


@dataclass(frozen=True)
class LoginCommand:
    """Команда входа."""

    email: str
    password: str


@dataclass(frozen=True)
class RefreshTokenCommand:
    """Команда обновления токенов."""

    refresh_token: str


@dataclass(frozen=True)
class TokenPair:
    """Пара JWT."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
