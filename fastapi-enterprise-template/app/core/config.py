from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "Production Backend App"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # PostgreSQL — individual fields ONLY, never DATABASE_URL
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "production_db"

    # Security
    SECRET_KEY: str = "change-me-in-production-use-a-long-random-string"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @property
    def DATABASE_URL(self) -> str:
        """
        Always construct URL here using quote_plus so special chars
        in passwords ($, @, !, #, &, *) are safely percent-encoded.
        NEVER read DATABASE_URL from environment — it breaks hostname resolution.
        """
        password = quote_plus(self.POSTGRES_PASSWORD)
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{password}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
