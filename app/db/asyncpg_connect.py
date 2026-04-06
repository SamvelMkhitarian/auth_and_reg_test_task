from sqlalchemy.engine.url import make_url


def connect_args_for_database_url(database_url: str) -> dict:
    if not database_url.startswith("postgresql+asyncpg"):
        return {}
    if "ssl" in make_url(database_url).query:
        return {}
    return {"ssl": False}
