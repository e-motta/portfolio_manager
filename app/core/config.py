from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = "a89fdb83be9832133abca00a6420cfd5448e194449a272ed2d8a3f938254aecc"

    DATABASE_URL: str = "sqlite:///./local.db"
    TEST_DATABASE_URL: str = "sqlite:///:memory:"

    FIRST_SUPERUSER_USERNAME: str = "admin"
    FIRST_SUPERUSER_PASSWORD: str = "Admin12@"
    FIRST_SUPERUSER_EMAIL: str = "admin@example.com"
    FIRST_SUPERUSER_FIRST_NAME: str = "First"
    FIRST_SUPERUSER_LAST_NAME: str = "Superuser"

    AUTH_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    API_V1_STR: str = "/api/v1"
    USERS_ROUTE_STR: str = "users"
    ACCOUNTS_ROUTE_STR: str = "accounts"
    STOCKS_ROUTE_STR: str = "stocks"
    TRADES_ROUTE_STR: str = "trades"
    LEDGER_ROUTE_STR: str = "ledger"

    USERNAME_MAX_LENGTH: int = 30


settings = Settings()
