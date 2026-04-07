from pydantic import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    OPENAI_BASE_URL : str = "https://api.openai.com/v1"
    TIMEOUT : int = 0
    
    class Config:
        env_file = ".env"
        
settings = Settings()