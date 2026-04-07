import httpx
from app.core.config import settings

class OpenAIClient:
    def __init__(self) -> None:
        self.base_url = settings.OPENAI_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
    async def chat(self, messages:list[str]):
        async with httpx.AsyncClient(timeout=settings.TIMEOUT) as client:
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