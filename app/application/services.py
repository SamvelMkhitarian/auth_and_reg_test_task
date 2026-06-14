from app.application.ports import PasswordHasherPort, TokenServicePort, UserRepositoryPort
from app.domain.entities import LoginData, RegisterData, TokenPair, UpdateProfileData, User
from app.domain.enums import UserRole
from app.domain.exceptions import (
    ForbiddenError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    UnauthorizedError,
)


class AuthService:
    """Сценарии регистрации, авторизации и профиля."""

    def __init__(
        self,
        repository: UserRepositoryPort,
        password_hasher: PasswordHasherPort,
        token_service: TokenServicePort,
    ) -> None:
        self._repository = repository
        self._hasher = password_hasher
        self._tokens = token_service

    async def register(self, data: RegisterData) -> User:
        email = data.email.strip().lower()
        user = User(
            id=None,
            email=email,
            password_hash=self._hasher.hash(data.password),
            full_name=None,
            phone=None,
            role=UserRole.free_user,
            is_active=True,
        )
        created = await self._repository.add(user)
        await self._repository.log_audit(
            action="register",
            user_id=created.id,
            detail=f"email={email}",
        )
        return created

    async def login(self, data: LoginData) -> TokenPair:
        email = data.email.strip().lower()
        user = await self._repository.get_by_email(email)
        if user is None or not user.is_active or user.id is None:
            raise InvalidCredentialsError
        if not self._hasher.verify(data.password, user.password_hash):
            raise InvalidCredentialsError
        tokens = self._issue_tokens(user.id)
        await self._repository.log_audit(action="login", user_id=user.id, detail="success")
        return tokens

    async def refresh(self, refresh_token: str) -> TokenPair:
        try:
            claims = self._tokens.parse_refresh_claims(refresh_token)
        except ValueError as exc:
            raise InvalidRefreshTokenError from exc
        user = await self._repository.get_by_id(claims.subject_user_id)
        if user is None or not user.is_active or user.id is None:
            raise InvalidRefreshTokenError
        return self._issue_tokens(user.id)

    async def get_current_user(self, access_token: str) -> User:
        try:
            claims = self._tokens.parse_access_claims(access_token)
        except ValueError as exc:
            raise UnauthorizedError from exc
        user = await self._repository.get_by_id(claims.subject_user_id)
        if user is None or not user.is_active:
            raise UnauthorizedError
        return user

    async def update_profile(self, user: User, data: UpdateProfileData) -> User:
        if data.full_name is not None:
            user.full_name = data.full_name
        if data.phone is not None:
            user.phone = data.phone
        return await self._repository.update(user)

    async def list_all_users(self, caller: User) -> list[User]:
        if caller.role != UserRole.admin:
            raise ForbiddenError
        return await self._repository.list_all()

    def _issue_tokens(self, user_id: int) -> TokenPair:
        return TokenPair(
            access_token=self._tokens.create_access_token(user_id),
            refresh_token=self._tokens.create_refresh_token(user_id),
        )
