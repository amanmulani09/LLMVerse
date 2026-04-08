import httpx
from fastapi import Depends
from functools import lru_cache
from app.core.config import get_setting, Settings
class OpenAIClient:
    def __init__(self, settings:Settings) -> None:
        self.settings = settings
        self.base_url = settings.OPENAI_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
    async def chat(self, messages:list[dict[str,str]]):
        async with httpx.AsyncClient(timeout=self.settings.TIMEOUT) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model":"gpt-4o-mini",
                    "messages":messages,
                },
            )
            response.raise_for_status()
            return response.json()
        

@lru_cache
def get_openai_client(settings:Settings = Depends(get_setting)):
    return OpenAIClient(settings)