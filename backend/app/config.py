"""
Application configuration using Pydantic Settings.
"""
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "SarkariSach"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    DATABASE_URL: str = "sqlite:///./sarkarisach.db"
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"
    ]
    RATE_LIMIT_PER_MINUTE: str = "30/minute"
    MAX_FILE_SIZE_MB: int = 10
    TELEGRAM_BOT_TOKEN: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
