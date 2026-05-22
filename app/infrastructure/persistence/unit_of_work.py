from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.unit_of_work import IUnitOfWork
from app.infrastructure.persistence.repositories.audit_repository import SqlAlchemyAuditRepository
from app.infrastructure.persistence.repositories.user_repository import SqlAlchemyUserRepository


class SqlAlchemyUnitOfWork(IUnitOfWork):
    """Единица работы: одна сессия, общий commit/rollback."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self.users = SqlAlchemyUserRepository(session)
        self.audit = SqlAlchemyAuditRepository(session)

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
