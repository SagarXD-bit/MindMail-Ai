"""Application configuration loaded from environment variables."""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    database_url: str = "sqlite:///./mailmind.db"
    db_host: str = "127.0.0.1"
    db_port: str = "3306"
    db_name: str = "mailmind"
    db_user: str = "root"
    db_password: str = ""

    # AI / OpenAI
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"

    # Security
    email_encryption_key: str = ""

    # App
    app_env: str = "development"
    cors_origins: str = "*"

    @property
    def resolved_database_url(self) -> str:
        """Build the MySQL connection URL from Render environment variables."""
        from urllib.parse import quote_plus

        if self.db_host and self.db_user:
            pwd = quote_plus(self.db_password)

            return (
                f"mysql+pymysql://{self.db_user}:{pwd}@"
                f"{self.db_host}:{self.db_port}/{self.db_name}"
            )

        return self.database_url


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
