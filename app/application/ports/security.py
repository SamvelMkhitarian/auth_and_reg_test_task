from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class TokenClaims:
    """Распарсенные claims JWT."""

    subject_user_id: int
    token_type: str


class IPasswordHasher(Protocol):
    """Порт хеширования паролей."""

    def hash(self, plain_password: str) -> str: ...

    def verify(self, plain_password: str, password_hash: str) -> bool: ...


class ITokenService(Protocol):
    """Порт выпуска и проверки JWT."""

    def create_access_token(self, user_id: int) -> str: ...

    def create_refresh_token(self, user_id: int) -> str: ...

    def decode(self, token: str) -> dict[str, Any]: ...

    def parse_refresh_claims(self, token: str) -> TokenClaims: ...

    def parse_access_claims(self, token: str) -> TokenClaims: ...
