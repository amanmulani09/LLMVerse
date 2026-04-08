"""
Chat API endpoints for LLMVerse application.

This module provides REST API endpoints for chat interactions
with proper error handling and validation.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from app.schemas.chat import ChatRequest, ChatResponse, ErrorResponse
from app.services.llm_service import LLMService, get_llm_service
from app.core.logging_config import get_logger
from app.core.exceptions import (
    ValidationError,
    LLMProviderError,
    RateLimitError,
    AuthenticationError,
    TimeoutError,
    ServiceUnavailableError
)

logger = get_logger(__name__)
router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        401: {"model": ErrorResponse, "description": "Authentication error"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
        503: {"model": ErrorResponse, "description": "Service unavailable"}
    },
    summary="Chat with LLM",
    description="Send a message to the LLM and receive a response"
)
async def chat(
    request: ChatRequest,
    http_request: Request,
    llm_service: LLMService = Depends(get_llm_service)
) -> ChatResponse:
    """
    Chat endpoint for LLM interactions.
    
    Args:
        request: Chat request with user message.
        http_request: FastAPI request object for accessing request ID.
        llm_service: LLM service dependency.
        
    Returns:
        Chat response with LLM generated text.
        
    Raises:
        HTTPException: For various error conditions.
    """
    request_id = getattr(http_request.state, "request_id", None)
    
    try:
        logger.info(
            "Processing chat request",
            extra={
                "request_id": request_id,
                "message_length": len(request.message)
            }
        )
        
        # Generate response
        response_text = await llm_service.generate_response(request.message)
        
        logger.info(
            "Chat request completed successfully",
            extra={
                "request_id": request_id,
                "response_length": len(response_text)
            }
        )
        
        return ChatResponse(
            response=response_text,
            request_id=request_id
        )
    
    except ValidationError as e:
        logger.warning(
            f"Validation error: {e.message}",
            extra={"request_id": request_id, "details": e.details}
        )
        raise HTTPException(
            status_code=400,
            detail={
                "error": "validation_error",
                "message": e.message,
                "details": e.details,
                "request_id": request_id
            }
        )
    
    except AuthenticationError as e:
        logger.error(
            f"Authentication error: {e.message}",
            extra={"request_id": request_id}
        )
        raise HTTPException(
            status_code=401,
            detail={
                "error": "authentication_error",
                "message": "Failed to authenticate with LLM provider",
                "request_id": request_id
            }
        )
    
    except RateLimitError as e:
        logger.warning(
            f"Rate limit exceeded: {e.message}",
            extra={"request_id": request_id}
        )
        raise HTTPException(
            status_code=429,
            detail={
                "error": "rate_limit_error",
                "message": "Rate limit exceeded. Please try again later.",
                "request_id": request_id
            }
        )
    
    except TimeoutError as e:
        logger.error(
            f"Request timeout: {e.message}",
            extra={"request_id": request_id}
        )
        raise HTTPException(
            status_code=504,
            detail={
                "error": "timeout_error",
                "message": "Request timed out. Please try again.",
                "request_id": request_id
            }
        )
    
    except ServiceUnavailableError as e:
        logger.error(
            f"Service unavailable: {e.message}",
            extra={"request_id": request_id}
        )
        raise HTTPException(
            status_code=503,
            detail={
                "error": "service_unavailable",
                "message": "LLM service is temporarily unavailable. Please try again later.",
                "request_id": request_id
            }
        )
    
    except LLMProviderError as e:
        logger.error(
            f"LLM provider error: {e.message}",
            extra={"request_id": request_id, "details": e.details},
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error": "llm_provider_error",
                "message": "An error occurred while processing your request",
                "request_id": request_id
            }
        )
    
    except Exception as e:
        logger.error(
            f"Unexpected error: {str(e)}",
            extra={"request_id": request_id},
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": "An unexpected error occurred",
                "request_id": request_id
            }
        )
