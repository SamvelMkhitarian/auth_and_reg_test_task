from fastapi import APIRouter, HTTPException, Request, status

from app.domain.entities import LoginData, RegisterData, UpdateProfileData
from app.domain.exceptions import (
    EmailAlreadyRegisteredError,
    ForbiddenError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
)
from app.presentation.api.dependencies import AuthServiceDep, CurrentUserDep
from app.presentation.api.schemas import (
    LoginIn,
    RefreshIn,
    RegisterIn,
    TokenPairOut,
    UserProfileOut,
    UserUpdateIn,
)
from app.rate_limit import limiter

auth_router = APIRouter(prefix="/auth", tags=["auth"])
users_router = APIRouter(prefix="/users", tags=["users"])


@auth_router.post(
    "/register",
    response_model=UserProfileOut,
    status_code=status.HTTP_201_CREATED,
)
async def register(body: RegisterIn, service: AuthServiceDep) -> UserProfileOut:
    try:
        user = await service.register(RegisterData(email=str(body.email), password=body.password))
    except EmailAlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        ) from None
    return UserProfileOut.from_entity(user)


@auth_router.post("/login", response_model=TokenPairOut)
@limiter.limit("5/minute")
async def login(
    request: Request,  # noqa: F841
    body: LoginIn,
    service: AuthServiceDep,
) -> TokenPairOut:
    try:
        tokens = await service.login(LoginData(email=str(body.email), password=body.password))
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        ) from None
    return TokenPairOut.from_entity(tokens)


@auth_router.post("/refresh", response_model=TokenPairOut)
async def refresh_tokens(body: RefreshIn, service: AuthServiceDep) -> TokenPairOut:
    try:
        tokens = await service.refresh(body.refresh_token)
    except InvalidRefreshTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        ) from None
    return TokenPairOut.from_entity(tokens)


@users_router.get("/me", response_model=UserProfileOut)
async def read_me(current_user: CurrentUserDep) -> UserProfileOut:
    return UserProfileOut.from_entity(current_user)


@users_router.put("/me", response_model=UserProfileOut)
async def update_me(
    body: UserUpdateIn,
    service: AuthServiceDep,
    current_user: CurrentUserDep,
) -> UserProfileOut:
    updated = await service.update_profile(
        current_user,
        UpdateProfileData(full_name=body.full_name, phone=body.phone),
    )
    return UserProfileOut.from_entity(updated)


@users_router.get("/", response_model=list[UserProfileOut])
async def read_all_users(
    service: AuthServiceDep,
    current_user: CurrentUserDep,
) -> list[UserProfileOut]:
    try:
        users = await service.list_all_users(current_user)
    except ForbiddenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        ) from None
    return [UserProfileOut.from_entity(user) for user in users]
