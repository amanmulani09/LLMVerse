"""
LLM service for handling chat interactions.

This module provides the business logic layer for LLM interactions,
including retry logic, prompt management, and response processing.
"""

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from fastapi import Depends
from app.clients.openai_client import OpenAIClient, get_openai_client
from app.core.config import get_settings, Settings
from app.core.logging_config import get_logger
from app.core.exceptions import (
    RateLimitError,
    TimeoutError,
    ServiceUnavailableError
)

logger = get_logger(__name__)


class LLMService:
    """Service for managing LLM interactions."""
    
    def __init__(self, client: OpenAIClient, settings: Settings) -> None:
        """
        Initialize LLM service.
        
        Args:
            client: OpenAI client instance.
            settings: Application settings.
        """
        self.client = client
        self.settings = settings
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((RateLimitError, TimeoutError, ServiceUnavailableError)),
        reraise=True
    )
    async def generate_response(
        self,
        user_input: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None
    ) -> str:
        """
        Generate a response from the LLM.
        
        This method includes automatic retry logic for transient errors
        like rate limits, timeouts, and service unavailability.
        
        Args:
            user_input: User's message/question.
            system_prompt: Optional system prompt override.
            temperature: Sampling temperature (0-2).
            max_tokens: Maximum tokens in response.
            
        Returns:
            Generated response text.
            
        Raises:
            LLMProviderError: If LLM provider returns an error.
            ValidationError: If input validation fails.
        """
        # Use default system prompt if not provided
        if system_prompt is None:
            system_prompt = self.settings.DEFAULT_SYSTEM_PROMPT
        
        # Build messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        logger.info(
            "Generating LLM response",
            extra={
                "user_input_length": len(user_input),
                "system_prompt_length": len(system_prompt)
            }
        )
        
        try:
            # Call OpenAI API
            response = await self.client.chat(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Extract response text
            response_text = response["choices"][0]["message"]["content"]
            
            logger.info(
                "Successfully generated LLM response",
                extra={"response_length": len(response_text)}
            )
            
            return response_text
            
        except Exception as e:
            logger.error(
                f"Failed to generate LLM response: {str(e)}",
                exc_info=True
            )
            raise


def get_llm_service(
    client: OpenAIClient = Depends(get_openai_client),
    settings: Settings = Depends(get_settings)
) -> LLMService:
    """
    Get LLM service instance.
    
    Args:
        client: OpenAI client dependency.
        settings: Application settings dependency.
        
    Returns:
        LLM service instance.
    """
    return LLMService(client, settings)
