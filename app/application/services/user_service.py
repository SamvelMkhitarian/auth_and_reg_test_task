from app.application.dto.user import UpdateProfileCommand
from app.application.exceptions import ForbiddenError, UnauthorizedError
from app.application.ports.security import ITokenService
from app.application.ports.unit_of_work import IUnitOfWork
from app.domain.entities.user import User
from app.domain.enums.user_role import UserRole


class UserService:
    """Сценарии профиля и администрирования пользователей."""

    def __init__(self, uow: IUnitOfWork, token_service: ITokenService) -> None:
        self._uow = uow
        self._tokens = token_service

    async def resolve_access_token(self, access_token: str) -> User:
        try:
            claims = self._tokens.parse_access_claims(access_token)
        except ValueError as exc:
            raise UnauthorizedError from exc
        user = await self._uow.users.get_by_id(claims.subject_user_id)
        if user is None or not user.is_active:
            raise UnauthorizedError
        return user

    async def update_profile(self, user: User, command: UpdateProfileCommand) -> User:
        if command.full_name is not None:
            user.full_name = command.full_name
        if command.phone is not None:
            user.phone = command.phone
        return await self._uow.users.update(user)

    async def list_all_users(self, caller: User) -> list[User]:
        if caller.role != UserRole.admin:
            raise ForbiddenError
        return await self._uow.users.list_all()
