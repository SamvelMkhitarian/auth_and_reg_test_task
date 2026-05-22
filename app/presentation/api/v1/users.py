from fastapi import APIRouter

from app.application.dto.user import UpdateProfileCommand
from app.application.exceptions import ForbiddenError
from app.presentation.api.deps import CurrentUserDep, UnitOfWorkDep, UserServiceDep, raise_forbidden
from app.presentation.mappers import user_mapper
from app.presentation.schemas.user import UserProfileOut, UserUpdateIn

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserProfileOut)
async def read_me(current_user: CurrentUserDep) -> UserProfileOut:
    """Профиль текущего пользователя."""
    return user_mapper.to_profile_out(current_user)


@router.put("/me", response_model=UserProfileOut)
async def update_me(
    body: UserUpdateIn,
    user_service: UserServiceDep,
    current_user: CurrentUserDep,
    uow: UnitOfWorkDep,
) -> UserProfileOut:
    """Обновление имени и телефона."""
    updated = await user_service.update_profile(
        current_user,
        UpdateProfileCommand(full_name=body.full_name, phone=body.phone),
    )
    await uow.commit()
    return user_mapper.to_profile_out(updated)


@router.get("/", response_model=list[UserProfileOut])
async def read_all_users(
    user_service: UserServiceDep,
    current_user: CurrentUserDep,
) -> list[UserProfileOut]:
    """Список всех пользователей (только для админа)."""
    try:
        users = await user_service.list_all_users(current_user)
    except ForbiddenError as exc:
        raise_forbidden(exc)
    return [user_mapper.to_profile_out(u) for u in users]
