from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.security import IPasswordHasher, ITokenService
from app.application.ports.unit_of_work import IUnitOfWork
from app.application.services.auth_service import AuthService
from app.application.services.user_service import UserService
from app.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork
from app.infrastructure.security.bcrypt_password_hasher import BcryptPasswordHasher
from app.infrastructure.security.jwt_token_service import JwtTokenService


@lru_cache
def get_password_hasher() -> IPasswordHasher:
    return BcryptPasswordHasher()


@lru_cache
def get_token_service() -> ITokenService:
    return JwtTokenService()


def build_unit_of_work(session: AsyncSession) -> IUnitOfWork:
    return SqlAlchemyUnitOfWork(session)


def build_auth_service(uow: IUnitOfWork) -> AuthService:
    return AuthService(
        uow=uow,
        password_hasher=get_password_hasher(),
        token_service=get_token_service(),
    )


def build_user_service(uow: IUnitOfWork) -> UserService:
    return UserService(uow=uow, token_service=get_token_service())
