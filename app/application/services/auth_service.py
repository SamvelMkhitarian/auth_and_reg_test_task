from app.application.dto.auth import (
    LoginCommand,
    RefreshTokenCommand,
    RegisterUserCommand,
    TokenPair,
)
from app.application.exceptions import (
    DuplicateEmailError,
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
)
from app.application.ports.security import IPasswordHasher, ITokenService
from app.application.ports.unit_of_work import IUnitOfWork
from app.domain.entities.user import User
from app.domain.enums.user_role import UserRole


class AuthService:
    """Сценарии регистрации, входа и обновления токенов."""

    def __init__(
        self,
        uow: IUnitOfWork,
        password_hasher: IPasswordHasher,
        token_service: ITokenService,
    ) -> None:
        self._uow = uow
        self._hasher = password_hasher
        self._tokens = token_service

    async def register(self, command: RegisterUserCommand) -> User:
        email = command.email.strip().lower()
        user = User(
            id=None,
            email=email,
            password_hash=self._hasher.hash(command.password),
            full_name=None,
            phone=None,
            role=UserRole.free_user,
            is_active=True,
        )
        try:
            created = await self._uow.users.add(user)
        except DuplicateEmailError as exc:
            raise EmailAlreadyRegisteredError from exc
        await self._uow.audit.log(
            action="register",
            user_id=created.id,
            detail=f"email={email}",
        )
        return created

    async def login(self, command: LoginCommand) -> TokenPair:
        email = command.email.strip().lower()
        user = await self._uow.users.get_by_email(email)
        if user is None or not user.is_active:
            raise InvalidCredentialsError
        if not self._hasher.verify(command.password, user.password_hash):
            raise InvalidCredentialsError
        if user.id is None:
            raise InvalidCredentialsError
        tokens = self._issue_tokens(user.id)
        await self._uow.audit.log(
            action="login",
            user_id=user.id,
            detail="success",
        )
        return tokens

    async def refresh(self, command: RefreshTokenCommand) -> TokenPair:
        try:
            claims = self._tokens.parse_refresh_claims(command.refresh_token)
        except ValueError as exc:
            raise InvalidRefreshTokenError from exc
        user = await self._uow.users.get_by_id(claims.subject_user_id)
        if user is None or not user.is_active:
            raise InvalidRefreshTokenError
        if user.id is None:
            raise InvalidRefreshTokenError
        return self._issue_tokens(user.id)

    def _issue_tokens(self, user_id: int) -> TokenPair:
        return TokenPair(
            access_token=self._tokens.create_access_token(user_id),
            refresh_token=self._tokens.create_refresh_token(user_id),
        )
