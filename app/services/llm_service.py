from tenacity import retry, stop_after_attempt, wait_exponential
from functools import lru_cache
from app.clients.openai_client import OpenAIClient, get_openai_client
from fastapi import Depends
class LLMService:
    
    def __init__(self, client:OpenAIClient) -> None:
        self.client = client
        
    
    @retry(stop=stop_after_attempt(3),wait=wait_exponential(min=1,max=3))
    async def generate_response(self,user_input:str):
        
        messages = [
            {"role" : "system", "content":"You are very helpful"},
            {"role" : "user", "content":user_input}
        ]
        
        response = await self.client.chat(messages)
        return response["choices"][0]["message"]["content"]
    
@lru_cache
def get_llm_service(client: OpenAIClient = Depends(get_openai_client)):
    return LLMService(client)