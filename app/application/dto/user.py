from dataclasses import dataclass


@dataclass(frozen=True)
class UpdateProfileCommand:
    """Команда обновления профиля."""

    full_name: str | None
    phone: str | None
