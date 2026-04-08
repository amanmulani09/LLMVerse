from fastapi import APIRouter, HTTPException, Depends
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm_service import LLMService, get_llm_service

router = APIRouter()
@router.post("/chat", response_model=ChatResponse)
async def chat(request:ChatRequest, llm_service:LLMService = Depends(get_llm_service)):
    try: 
        response = await llm_service.generate_response(request.message)
        return ChatResponse(response=response)
    
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))