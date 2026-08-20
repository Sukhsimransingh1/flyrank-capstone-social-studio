from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "flyrank-social-studio"
    app_env: str = "development"
    log_level: str = "INFO"

    database_url: str = (
        "postgresql+psycopg://socialstudio:socialstudio@db:5432/socialstudio"
    )

    publisher: str = "mock_x"

    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    scheduler_poll_interval: int = Field(
        default=5,
        ge=1,
        description="Scheduler polling interval in seconds.",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()