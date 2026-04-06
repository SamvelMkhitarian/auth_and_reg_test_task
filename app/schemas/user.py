from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserRegisterIn(BaseModel):
    """Тело регистрации."""

    model_config = ConfigDict(str_strip_whitespace=True, strict=True)

    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)


class UserProfileOut(BaseModel):
    """Профиль в ответах (без пароля)."""

    model_config = ConfigDict(from_attributes=True, strict=True)

    id: int
    email: str
    full_name: str | None
    phone: str | None
    role: UserRole
    is_active: bool
    created_at: datetime


class UserUpdateIn(BaseModel):
    """Обновление профиля."""

    model_config = ConfigDict(str_strip_whitespace=True, strict=True)

    full_name: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
