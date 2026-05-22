from typing import Protocol

from app.application.ports.repositories import IAuditRepository, IUserRepository


class IUnitOfWork(Protocol):
    """Порт единицы работы (транзакция + репозитории)."""

    users: IUserRepository
    audit: IAuditRepository

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...
