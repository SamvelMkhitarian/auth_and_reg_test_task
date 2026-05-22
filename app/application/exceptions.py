class ApplicationError(Exception):
    """Базовая ошибка прикладного слоя."""


class DuplicateEmailError(ApplicationError):
    """Нарушение уникальности email на уровне персистентности."""


class EmailAlreadyRegisteredError(ApplicationError):
    """Email уже зарегистрирован."""


class InvalidCredentialsError(ApplicationError):
    """Неверный email или пароль."""


class InvalidRefreshTokenError(ApplicationError):
    """Невалидный или просроченный refresh token."""


class UnauthorizedError(ApplicationError):
    """Пользователь не аутентифицирован или токен недействителен."""


class ForbiddenError(ApplicationError):
    """Недостаточно прав."""
