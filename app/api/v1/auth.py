import structlog
from fastapi import APIRouter, HTTPException, Request, status

from app.api.deps import SessionDep
from app.rate_limit import limiter
from app.schemas.auth import LoginIn, RefreshIn, TokenPairOut
from app.schemas.user import UserProfileOut, UserRegisterIn
from app.use_cases.auth import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    login_user,
    refresh_access_token,
    register_user,
)

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserProfileOut,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    body: UserRegisterIn,
    session: SessionDep,
) -> UserProfileOut:
    """Регистрация по email и паролю."""
    try:
        user = await register_user(session, body)
    except EmailAlreadyRegisteredError:
        logger.info("register_conflict", email=body.email)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        ) from None
    await session.commit()
    return UserProfileOut.model_validate(user)


@router.post("/login", response_model=TokenPairOut)
@limiter.limit("5/minute")
async def login(
    request: Request,  # noqa: F841
    body: LoginIn,
    session: SessionDep,
) -> TokenPairOut:
    """Логин: access + refresh JWT. Не более 5 попыток в минуту с одного IP."""
    try:
        tokens = await login_user(session, body.email, body.password)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        ) from None
    await session.commit()
    return tokens


@router.post("/refresh", response_model=TokenPairOut)
async def refresh_tokens(
    body: RefreshIn,
    session: SessionDep,
) -> TokenPairOut:
    """Новая пара токенов по refresh."""
    try:
        tokens = await refresh_access_token(session, body.refresh_token)
    except InvalidRefreshTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        ) from None
    await session.commit()
    return tokens
