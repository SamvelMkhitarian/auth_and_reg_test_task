import structlog
from fastapi import APIRouter, HTTPException, Request, status

from app.application.dto.auth import LoginCommand, RefreshTokenCommand, RegisterUserCommand
from app.application.exceptions import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
)
from app.presentation.api.deps import AuthServiceDep, UnitOfWorkDep
from app.presentation.mappers import user_mapper
from app.presentation.schemas.auth import LoginIn, RefreshIn, TokenPairOut
from app.presentation.schemas.user import UserProfileOut, UserRegisterIn
from app.rate_limit import limiter

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserProfileOut,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    body: UserRegisterIn,
    auth_service: AuthServiceDep,
    uow: UnitOfWorkDep,
) -> UserProfileOut:
    """Регистрация по email и паролю."""
    try:
        user = await auth_service.register(
            RegisterUserCommand(email=str(body.email), password=body.password)
        )
    except EmailAlreadyRegisteredError:
        logger.info("register_conflict", email=body.email)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        ) from None
    await uow.commit()
    return user_mapper.to_profile_out(user)


@router.post("/login", response_model=TokenPairOut)
@limiter.limit("5/minute")
async def login(
    request: Request,  # noqa: F841
    body: LoginIn,
    auth_service: AuthServiceDep,
    uow: UnitOfWorkDep,
) -> TokenPairOut:
    """Логин: access + refresh JWT. Не более 5 попыток в минуту с одного IP."""
    try:
        tokens = await auth_service.login(
            LoginCommand(email=str(body.email), password=body.password)
        )
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        ) from None
    await uow.commit()
    return user_mapper.to_token_pair_out(tokens)


@router.post("/refresh", response_model=TokenPairOut)
async def refresh_tokens(
    body: RefreshIn,
    auth_service: AuthServiceDep,
    uow: UnitOfWorkDep,
) -> TokenPairOut:
    """Новая пара токенов по refresh."""
    try:
        tokens = await auth_service.refresh(RefreshTokenCommand(refresh_token=body.refresh_token))
    except InvalidRefreshTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        ) from None
    await uow.commit()
    return user_mapper.to_token_pair_out(tokens)
