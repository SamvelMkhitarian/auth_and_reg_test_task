from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserUpdateIn


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    """Возвращает пользователя по id."""
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    """Возвращает пользователя по email (без учёта регистра — email в БД в нижнем регистре)."""
    normalized = email.strip().lower()
    result = await session.execute(select(User).where(User.email == normalized))
    return result.scalar_one_or_none()


async def update_user_profile(
    session: AsyncSession,
    user: User,
    data: UserUpdateIn,
) -> User:
    """Обновляет имя и телефон."""
    if data.full_name is not None:
        user.full_name = data.full_name
    if data.phone is not None:
        user.phone = data.phone
    await session.flush()
    await session.refresh(user)
    return user
