from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.domain.entities import TokenPair, User
from app.domain.enums import UserRole


class RegisterIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, strict=True)

    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)


class LoginIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, strict=True)

    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=1, max_length=128)


class RefreshIn(BaseModel):
    model_config = ConfigDict(strict=True)

    refresh_token: str = Field(min_length=10)


class TokenPairOut(BaseModel):
    model_config = ConfigDict(strict=True)

    access_token: str
    refresh_token: str
    token_type: str = "bearer"

    @classmethod
    def from_entity(cls, tokens: TokenPair) -> "TokenPairOut":
        return cls(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            token_type=tokens.token_type,
        )


class UserProfileOut(BaseModel):
    model_config = ConfigDict(strict=True)

    id: int
    email: str
    full_name: str | None
    phone: str | None
    role: UserRole
    is_active: bool
    created_at: datetime

    @classmethod
    def from_entity(cls, user: User) -> "UserProfileOut":
        if user.id is None or user.created_at is None:
            raise ValueError("Persisted user required for profile response")
        return cls(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
        )


class UserUpdateIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, strict=True)

    full_name: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
