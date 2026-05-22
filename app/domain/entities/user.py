from dataclasses import dataclass
from datetime import datetime

from app.domain.enums.user_role import UserRole


@dataclass
class User:
    """Доменная сущность пользователя."""

    id: int | None
    email: str
    password_hash: str
    full_name: str | None
    phone: str | None
    role: UserRole
    is_active: bool
    created_at: datetime | None = None
