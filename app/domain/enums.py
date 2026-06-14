from enum import StrEnum


class UserRole(StrEnum):
    free_user = "free_user"
    paid_user = "paid_user"
    specialist = "specialist"
    admin = "admin"
