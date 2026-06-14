from dataclasses import dataclass
from datetime import datetime

from app.domain.enums import UserRole


@dataclass(slots=True)
class User:
    id: int | None
    email: str
    password_hash: str
    full_name: str | None
    phone: str | None
    role: UserRole
    is_active: bool
    created_at: datetime | None = None


@dataclass(slots=True)
class RegisterData:
    email: str
    password: str


@dataclass(slots=True)
class LoginData:
    email: str
    password: str


@dataclass(slots=True)
class TokenPair:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@dataclass(slots=True)
class UpdateProfileData:
    full_name: str | None = None
    phone: str | None = None
