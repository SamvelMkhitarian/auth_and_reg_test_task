from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.exceptions import ForbiddenError, UnauthorizedError
from app.application.ports.unit_of_work import IUnitOfWork
from app.application.services.auth_service import AuthService
from app.application.services.user_service import UserService
from app.composition.container import build_auth_service, build_unit_of_work, build_user_service
from app.domain.entities.user import User
from app.infrastructure.persistence.database.session import get_session

security = HTTPBearer(auto_error=False)

SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_unit_of_work(session: SessionDep) -> IUnitOfWork:
    """Единица работы на один HTTP-запрос."""
    return build_unit_of_work(session)


UnitOfWorkDep = Annotated[IUnitOfWork, Depends(get_unit_of_work)]


async def get_auth_service(uow: UnitOfWorkDep) -> AuthService:
    return build_auth_service(uow)


async def get_user_service(uow: UnitOfWorkDep) -> UserService:
    return build_user_service(uow)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]


async def get_current_user(
    user_service: UserServiceDep,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> User:
    """Текущий пользователь по access JWT."""
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return await user_service.resolve_access_token(credentials.credentials)
    except UnauthorizedError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None


CurrentUserDep = Annotated[User, Depends(get_current_user)]


def raise_forbidden(exc: ForbiddenError) -> None:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Admin access required",
    ) from exc
