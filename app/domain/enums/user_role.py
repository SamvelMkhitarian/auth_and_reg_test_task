import enum


class UserRole(str, enum.Enum):
    """Роль пользователя."""

    free_user = "free_user"
    paid_user = "paid_user"
    specialist = "specialist"
    admin = "admin"
