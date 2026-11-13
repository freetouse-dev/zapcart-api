from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Zapcart Application"
    app_version: str = "1.0.0"
    app_environment: str = "development"
    api_prefix: str = "/api/v1"

    db_host: str = "localhost"
    db_user: str = "postgres"
    db_port: int = 5432
    db_password: str = "your_database_password"
    db_name: str = "your_database_name"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    jwt_secret_key: str = "your_jwt_secret_key"
    jwt_algorithm: str = "HS256"
    jwt_expire_time: int = 30

    redis_url: str = "redis://localhost:6379/0"
    cors_origins: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
