"""
OpenAI API client for LLMVerse application.

This module provides a properly configured HTTP client for interacting
with OpenAI's API, including connection pooling and error handling.
"""

import httpx
from typing import Any
from fastapi import Depends
from app.core.config import get_settings, Settings
from app.core.logging_config import get_logger
from app.core.exceptions import (
    LLMProviderError,
    RateLimitError,
    AuthenticationError,
    TimeoutError as CustomTimeoutError,
    ServiceUnavailableError
)

logger = get_logger(__name__)


class OpenAIClient:
    """Client for interacting with OpenAI API."""
    
    def __init__(self, settings: Settings) -> None:
        """
        Initialize OpenAI client with settings.
        
        Args:
            settings: Application settings containing API configuration.
        """
        self.settings = settings
        self.base_url = settings.OPENAI_BASE_URL
        self.model = settings.OPENAI_MODEL
        self.headers = {
            "Authorization": f"Bearer {self.settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Create a persistent HTTP client with connection pooling
        self._client: httpx.AsyncClient | None = None
    
    async def get_client(self) -> httpx.AsyncClient:
        """
        Get or create HTTP client with connection pooling.
        
        Returns:
            Configured async HTTP client.
        """
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=self.settings.OPENAI_TIMEOUT,
                limits=httpx.Limits(
                    max_keepalive_connections=5,
                    max_connections=10
                )
            )
        return self._client
    
    async def close(self) -> None:
        """Close the HTTP client and cleanup resources."""
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
    
    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None
    ) -> dict[str, Any]:
        """
        Send chat completion request to OpenAI API.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'.
            model: Optional model override (defaults to configured model).
            temperature: Sampling temperature (0-2).
            max_tokens: Maximum tokens in response.
            
        Returns:
            OpenAI API response as dictionary.
            
        Raises:
            AuthenticationError: If API key is invalid.
            RateLimitError: If rate limit is exceeded.
            TimeoutError: If request times out.
            ServiceUnavailableError: If OpenAI service is unavailable.
            LLMProviderError: For other API errors.
        """
        client = await self.get_client()
        
        payload: dict[str, Any] = {
            "model": model or self.model,
            "messages": messages,
            "temperature": temperature,
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        try:
            logger.info(
                f"Sending chat request to OpenAI",
                extra={
                    "model": payload["model"],
                    "message_count": len(messages)
                }
            )
            
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
            )
            
            # Handle different error status codes
            if response.status_code == 401:
                logger.error("OpenAI authentication failed")
                raise AuthenticationError(
                    "Invalid API key",
                    details={"status_code": response.status_code}
                )
            
            elif response.status_code == 429:
                logger.warning("OpenAI rate limit exceeded")
                raise RateLimitError(
                    "Rate limit exceeded",
                    details={"status_code": response.status_code}
                )
            
            elif response.status_code >= 500:
                logger.error(f"OpenAI service error: {response.status_code}")
                raise ServiceUnavailableError(
                    "OpenAI service unavailable",
                    details={"status_code": response.status_code}
                )
            
            # Raise for other error status codes
            response.raise_for_status()
            
            result = response.json()
            logger.info("Successfully received response from OpenAI")
            return result
            
        except httpx.TimeoutException as e:
            logger.error(f"OpenAI request timeout: {str(e)}")
            raise CustomTimeoutError(
                "Request to OpenAI timed out",
                details={"timeout": self.settings.OPENAI_TIMEOUT}
            )
        
        except httpx.HTTPStatusError as e:
            logger.error(f"OpenAI HTTP error: {str(e)}")
            raise LLMProviderError(
                f"OpenAI API error: {str(e)}",
                details={"status_code": e.response.status_code}
            )
        
        except Exception as e:
            logger.error(f"Unexpected error calling OpenAI: {str(e)}", exc_info=True)
            raise LLMProviderError(
                f"Unexpected error: {str(e)}",
                details={"error_type": type(e).__name__}
            )


# Global client instance
_openai_client: OpenAIClient | None = None


def get_openai_client(settings: Settings = Depends(get_settings)) -> OpenAIClient:
    """
    Get or create OpenAI client instance (singleton pattern).
    
    Args:
        settings: Application settings.
        
    Returns:
        OpenAI client instance.
    """
    global _openai_client
    
    if _openai_client is None:
        _openai_client = OpenAIClient(settings)
    
    return _openai_client


async def close_openai_client() -> None:
    """Close the global OpenAI client."""
    global _openai_client
    
    if _openai_client is not None:
        await _openai_client.close()
        _openai_client = None
