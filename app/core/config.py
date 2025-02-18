from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    USERNAME_MAX_LENGTH: int = 12


settings = Settings()
