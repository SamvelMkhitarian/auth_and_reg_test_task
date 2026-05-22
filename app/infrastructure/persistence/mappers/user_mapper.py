from app.domain.entities.user import User
from app.domain.enums.user_role import UserRole
from app.infrastructure.persistence.models.user import UserModel, UserRoleORM

_ROLE_TO_DOMAIN = {
    UserRoleORM.free_user: UserRole.free_user,
    UserRoleORM.paid_user: UserRole.paid_user,
    UserRoleORM.specialist: UserRole.specialist,
    UserRoleORM.admin: UserRole.admin,
}

_ROLE_TO_ORM = {v: k for k, v in _ROLE_TO_DOMAIN.items()}


def to_domain(model: UserModel) -> User:
    """ORM → доменная сущность."""
    return User(
        id=model.id,
        email=model.email,
        password_hash=model.password_hash,
        full_name=model.full_name,
        phone=model.phone,
        role=_ROLE_TO_DOMAIN[model.role],
        is_active=model.is_active,
        created_at=model.created_at,
    )


def to_model(entity: User) -> UserModel:
    """Доменная сущность → ORM (для insert/update)."""
    model = UserModel(
        email=entity.email,
        password_hash=entity.password_hash,
        full_name=entity.full_name,
        phone=entity.phone,
        role=_ROLE_TO_ORM[entity.role],
        is_active=entity.is_active,
    )
    if entity.id is not None:
        model.id = entity.id
    return model


def update_model_from_domain(model: UserModel, entity: User) -> None:
    """Копирует изменяемые поля домена в существующую ORM-запись."""
    model.full_name = entity.full_name
    model.phone = entity.phone
