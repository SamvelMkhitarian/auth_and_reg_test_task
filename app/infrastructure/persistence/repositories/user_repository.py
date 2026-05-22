from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.exceptions import DuplicateEmailError
from app.application.ports.repositories import IUserRepository
from app.domain.entities.user import User
from app.infrastructure.persistence.mappers import user_mapper
from app.infrastructure.persistence.models.user import UserModel


class SqlAlchemyUserRepository(IUserRepository):
    """Реализация IUserRepository через SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self._session.execute(select(UserModel).where(UserModel.id == user_id))
        model = result.scalar_one_or_none()
        return user_mapper.to_domain(model) if model else None

    async def get_by_email(self, email: str) -> User | None:
        normalized = email.strip().lower()
        result = await self._session.execute(
            select(UserModel).where(UserModel.email == normalized)
        )
        model = result.scalar_one_or_none()
        return user_mapper.to_domain(model) if model else None

    async def add(self, user: User) -> User:
        model = user_mapper.to_model(user)
        self._session.add(model)
        try:
            await self._session.flush()
        except IntegrityError as exc:
            await self._session.rollback()
            raise DuplicateEmailError from exc
        await self._session.refresh(model)
        return user_mapper.to_domain(model)

    async def update(self, user: User) -> User:
        if user.id is None:
            raise ValueError("User id is required for update")
        result = await self._session.execute(select(UserModel).where(UserModel.id == user.id))
        model = result.scalar_one()
        user_mapper.update_model_from_domain(model, user)
        await self._session.flush()
        await self._session.refresh(model)
        return user_mapper.to_domain(model)

    async def list_all(self) -> list[User]:
        result = await self._session.execute(select(UserModel).order_by(UserModel.id))
        return [user_mapper.to_domain(m) for m in result.scalars().all()]
