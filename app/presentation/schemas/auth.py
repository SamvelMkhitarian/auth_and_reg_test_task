from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginIn(BaseModel):
    """Логин."""

    model_config = ConfigDict(str_strip_whitespace=True, strict=True)

    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=1, max_length=128)


class TokenPairOut(BaseModel):
    """Пара JWT токенов."""

    model_config = ConfigDict(strict=True)

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshIn(BaseModel):
    """Обновление access token."""

    model_config = ConfigDict(strict=True)

    refresh_token: str = Field(min_length=10)
