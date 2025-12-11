from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


class DBSettings(BaseSettings):
    """
    Настройки базы данных (асинхронный PostgreSQL через asyncpg).
    """
    db_user: str = Field(alias="DB_USER")
    db_port: int = Field(alias="DB_PORT")
    db_password: str = Field(alias="DB_PASSWORD")
    db_host: str = Field(alias="DB_HOST")
    db_name: str = Field(alias="DB_NAME")
    db_show_query: bool = Field(default=False, alias="DB_SHOW_QUERY")

    @property
    def postgres_url_sync(self) -> str:
        """URL для sync SQLAlchemy (psycopg2)."""
        return (
            f"postgresql+psycopg2://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def postgres_url_async(self) -> str:
        """URL для async SQLAlchemy (asyncpg)."""
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )



class LLMSettings(BaseSettings):
    """
    Настройки LLM (сейчас использую Mistral).
    """
    llm_provider: str = Field(default="mistral", alias="LLM_PROVIDER")
    mistral_api_key: str = Field(alias="MISTRAL_API_KEY")
    mistral_model: str = Field(default="mistral-small-latest", alias="MISTRAL_MODEL")


class BotSettings(BaseSettings):
    """
    Настройки бота.
    """
    telegram_bot_token: str = Field(alias="TELEGRAM_BOT_TOKEN")


class Settings(BaseSettings):
    """
    Общие настройки приложения.
    """
    database: DBSettings = Field(default_factory=DBSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    bot: BotSettings = Field(default_factory=BotSettings)


@lru_cache
def get_settings() -> Settings:
    """Возвращает синглтон настроек приложения."""
    return Settings()


settings = get_settings()
