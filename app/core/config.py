"""
Configuration management for LLMVerse application.

This module handles all application settings using Pydantic Settings,
loading configuration from environment variables and .env file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_TIMEOUT: int = 30
    
    # Application Configuration
    APP_NAME: str = "LLMVerse"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # System Prompt Configuration
    DEFAULT_SYSTEM_PROMPT: str = "You are a helpful AI assistant."
    
    # Retry Configuration
    MAX_RETRIES: int = 3
    RETRY_MIN_WAIT: int = 1
    RETRY_MAX_WAIT: int = 10
    
    # Input Validation
    MAX_MESSAGE_LENGTH: int = 10000
    MIN_MESSAGE_LENGTH: int = 1
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True
    )


@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings.
    
    Returns:
        Settings: Application configuration instance.
    """
    return Settings()
