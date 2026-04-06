from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


async def log_action(
    session: AsyncSession,
    *,
    action: str,
    user_id: int | None = None,
    detail: str | None = None,
) -> None:
    """Пишет событие в audit_log: только add + flush; commit остаётся на стороне вызывающего кода."""
    entry = AuditLog(user_id=user_id, action=action, detail=detail)
    session.add(entry)
    await session.flush()
