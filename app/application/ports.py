from dataclasses import dataclass
from typing import Any, Protocol

from app.domain.entities import User


@dataclass(frozen=True)
class TokenClaims:
    subject_user_id: int
    token_type: str


class UserRepositoryPort(Protocol):
    async def get_by_id(self, user_id: int) -> User | None: ...

    async def get_by_email(self, email: str) -> User | None: ...

    async def add(self, user: User) -> User: ...

    async def update(self, user: User) -> User: ...

    async def list_all(self) -> list[User]: ...

    async def log_audit(
        self,
        *,
        action: str,
        user_id: int | None = None,
        detail: str | None = None,
    ) -> None: ...


class PasswordHasherPort(Protocol):
    def hash(self, plain_password: str) -> str: ...

    def verify(self, plain_password: str, password_hash: str) -> bool: ...


class TokenServicePort(Protocol):
    def create_access_token(self, user_id: int) -> str: ...

    def create_refresh_token(self, user_id: int) -> str: ...

    def decode(self, token: str) -> dict[str, Any]: ...

    def parse_refresh_claims(self, token: str) -> TokenClaims: ...

    def parse_access_claims(self, token: str) -> TokenClaims: ...
