from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    bot_token: str = Field(
        ...,
        description="Telegram Bot API token"
    )
    database_path: str = Field(
        default="quiz_bot.db",
        description="Path to SQLite database file"
    )

config: Config = Config()