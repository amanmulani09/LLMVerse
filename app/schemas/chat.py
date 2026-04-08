"""
Pydantic schemas for chat API endpoints.

This module defines request and response models with proper
validation and documentation.
"""

from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    
    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User message to send to the LLM",
        examples=["Hello, how are you?"]
    )
    
    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        """
        Validate and sanitize message.
        
        Args:
            v: Message string.
            
        Returns:
            Validated message.
            
        Raises:
            ValueError: If message is empty or only whitespace.
        """
        # Strip whitespace
        v = v.strip()
        
        # Check if empty after stripping
        if not v:
            raise ValueError("Message cannot be empty or only whitespace")
        
        return v
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "What is the capital of France?"
                }
            ]
        }
    }


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    
    response: str = Field(
        ...,
        description="LLM generated response",
        examples=["The capital of France is Paris."]
    )
    
    request_id: str | None = Field(
        None,
        description="Unique request identifier for tracking"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "response": "The capital of France is Paris.",
                    "request_id": "123e4567-e89b-12d3-a456-426614174000"
                }
            ]
        }
    }


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str = Field(
        ...,
        description="Error type or code"
    )
    
    message: str = Field(
        ...,
        description="Human-readable error message"
    )
    
    details: dict | None = Field(
        None,
        description="Additional error details"
    )
    
    request_id: str | None = Field(
        None,
        description="Request ID for tracking"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "error": "validation_error",
                    "message": "Message cannot be empty",
                    "details": {"field": "message"},
                    "request_id": "123e4567-e89b-12d3-a456-426614174000"
                }
            ]
        }
    }


class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: str = Field(
        ...,
        description="Service health status",
        examples=["healthy"]
    )
    
    version: str = Field(
        ...,
        description="Application version"
    )
    
    checks: dict[str, str] = Field(
        default_factory=dict,
        description="Individual component health checks"
    )
