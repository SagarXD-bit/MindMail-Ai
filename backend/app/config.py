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
        """Build the MySQL DATABASE_URL using PyMySQL when needed."""
        url = self.database_url

        # Use component variables when DATABASE_URL is a template,
        # missing, or SQLite.
        if not url or "{{" in url or "sqlite" in url:
            if self.db_host and self.db_user:
                from urllib.parse import quote_plus

                pwd = quote_plus(self.db_password)

                return (
                    f"mysql+pymysql://{self.db_user}:{pwd}@"
                    f"{self.db_host}:{self.db_port}/{self.db_name}"
                )

        # Force SQLAlchemy to use PyMySQL instead of MySQLdb.
        if url.startswith("mysql://"):
            return url.replace(
                "mysql://",
                "mysql+pymysql://",
                1,
            )

        return url


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
