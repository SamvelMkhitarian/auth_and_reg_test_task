class DomainError(Exception):
    """Базовое доменное исключение."""


class EmailAlreadyRegisteredError(DomainError):
    """Email уже зарегистрирован."""


class InvalidCredentialsError(DomainError):
    """Неверный email или пароль."""


class InvalidRefreshTokenError(DomainError):
    """Невалидный или просроченный refresh token."""


class UnauthorizedError(DomainError):
    """Пользователь не аутентифицирован или токен недействителен."""


class ForbiddenError(DomainError):
    """Недостаточно прав."""
