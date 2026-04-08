from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
class Settings(BaseSettings):
    OPENAI_API_KEY: str
    OPENAI_BASE_URL : str = "https://api.openai.com/v1"
    TIMEOUT : int = 0
    
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )
 
@lru_cache
def get_setting():
    return Settings()