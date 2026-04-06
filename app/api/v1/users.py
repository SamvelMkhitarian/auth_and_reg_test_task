from fastapi import APIRouter

from app.api.deps import CurrentUserDep, SessionDep
from app.models.user import User
from app.schemas.user import UserProfileOut, UserUpdateIn
from app.use_cases import user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserProfileOut)
async def read_me(
    current_user: CurrentUserDep,
) -> User:
    """Профиль текущего пользователя."""
    return current_user


@router.put("/me", response_model=UserProfileOut)
async def update_me(
    body: UserUpdateIn,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> User:
    """Обновление имени и телефона."""
    updated = await user.update_user_profile(session, current_user, body)
    await session.commit()
    return updated
