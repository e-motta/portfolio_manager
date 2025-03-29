import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", "a89fdb83be9832133abca00a6420cfd5448e194449a272ed2d8a3f938254aecc"
    )

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./local.db")
    TEST_DATABASE_URL: str = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")

    FIRST_SUPERUSER_USERNAME: str = os.getenv("FIRST_SUPERUSER_USERNAME", "admin")
    FIRST_SUPERUSER_PASSWORD: str = os.getenv("FIRST_SUPERUSER_PASSWORD", "Admin12@")
    FIRST_SUPERUSER_EMAIL: str = os.getenv("FIRST_SUPERUSER_EMAIL", "admin@example.com")
    FIRST_SUPERUSER_FIRST_NAME: str = os.getenv("FIRST_SUPERUSER_FIRST_NAME", "First")
    FIRST_SUPERUSER_LAST_NAME: str = os.getenv("FIRST_SUPERUSER_LAST_NAME", "Superuser")

    AUTH_ALGORITHM: str = os.getenv("AUTH_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")
    USERS_ROUTE_STR: str = os.getenv("USERS_ROUTE_STR", "users")
    ACCOUNTS_ROUTE_STR: str = os.getenv("ACCOUNTS_ROUTE_STR", "accounts")
    SECURITIES_ROUTE_STR: str = os.getenv("SECURITIES_ROUTE_STR", "securities")
    TRADES_ROUTE_STR: str = os.getenv("TRADES_ROUTE_STR", "trades")
    LEDGER_ROUTE_STR: str = os.getenv("LEDGER_ROUTE_STR", "ledger")

    USERNAME_MAX_LENGTH: int = int(os.getenv("USERNAME_MAX_LENGTH", 30))


settings = Settings()
