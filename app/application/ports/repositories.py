from typing import Protocol

from app.domain.entities.user import User


class IUserRepository(Protocol):
    """Порт доступа к пользователям."""

    async def get_by_id(self, user_id: int) -> User | None: ...

    async def get_by_email(self, email: str) -> User | None: ...

    async def add(self, user: User) -> User: ...

    async def update(self, user: User) -> User: ...

    async def list_all(self) -> list[User]: ...


class IAuditRepository(Protocol):
    """Порт записи аудита."""

    async def log(
        self,
        *,
        action: str,
        user_id: int | None = None,
        detail: str | None = None,
    ) -> None: ...
