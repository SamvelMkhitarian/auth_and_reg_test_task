from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.repositories import IAuditRepository
from app.infrastructure.persistence.models.audit_log import AuditLogModel


class SqlAlchemyAuditRepository(IAuditRepository):
    """Реализация IAuditRepository через SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def log(
        self,
        *,
        action: str,
        user_id: int | None = None,
        detail: str | None = None,
    ) -> None:
        entry = AuditLogModel(user_id=user_id, action=action, detail=detail)
        self._session.add(entry)
        await self._session.flush()
