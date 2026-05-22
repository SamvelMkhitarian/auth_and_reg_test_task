from app.application.dto.auth import TokenPair
from app.domain.entities.user import User
from app.domain.enums.user_role import UserRole
from app.presentation.schemas.auth import TokenPairOut
from app.presentation.schemas.user import UserProfileOut, UserRoleSchema

_ROLE_TO_SCHEMA = {
    UserRole.free_user: UserRoleSchema.free_user,
    UserRole.paid_user: UserRoleSchema.paid_user,
    UserRole.specialist: UserRoleSchema.specialist,
    UserRole.admin: UserRoleSchema.admin,
}


def to_profile_out(user: User) -> UserProfileOut:
    """Домен → HTTP DTO профиля."""
    if user.id is None or user.created_at is None:
        raise ValueError("Persisted user required for profile response")
    return UserProfileOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        role=_ROLE_TO_SCHEMA[user.role],
        is_active=user.is_active,
        created_at=user.created_at,
    )


def to_token_pair_out(tokens: TokenPair) -> TokenPairOut:
    """Application TokenPair → HTTP DTO."""
    return TokenPairOut(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type,
    )
