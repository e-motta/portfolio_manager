from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = "a89fdb83be9832133abca00a6420cfd5448e194449a272ed2d8a3f938254aecc"
    AUTH_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    API_V1_STR: str = "/api/v1"
    USERNAME_MAX_LENGTH: int = 12


settings = Settings()
