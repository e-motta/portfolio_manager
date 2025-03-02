from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = "a89fdb83be9832133abca00a6420cfd5448e194449a272ed2d8a3f938254aecc"
    AUTH_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    API_V1_STR: str = "/api/v1"
    USERS_ROUTE_STR: str = "users"
    ACCOUNTS_ROUTE_STR: str = "accounts"
    STOCKS_ROUTE_STR: str = "stocks"

    USERNAME_MAX_LENGTH: int = 12

    TEST_DATABASE_URL: str = "sqlite:///:memory:"


settings = Settings()
