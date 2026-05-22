import bcrypt

from app.application.ports.security import IPasswordHasher


class BcryptPasswordHasher(IPasswordHasher):
    """Bcrypt-адаптер IPasswordHasher."""

    def hash(self, plain_password: str) -> str:
        hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt(rounds=12))
        return hashed.decode("utf-8")

    def verify(self, plain_password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
