from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm_service import LLMService

router = APIRouter()
llm_service = LLMService()

@router.post("/chat", response_model=ChatResponse)
async def chat(request:ChatRequest):
    try: 
        response = await llm_service.generate_response(request.message)
        return ChatResponse(response=response)
    
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))