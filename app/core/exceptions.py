"""
Custom exceptions for LLMVerse application.

This module defines application-specific exceptions for better
error handling and more meaningful error messages.
"""

from typing import Any


class LLMVerseException(Exception):
    """Base exception for all LLMVerse errors."""
    
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        """
        Initialize exception.
        
        Args:
            message: Error message.
            details: Optional additional error details.
        """
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ConfigurationError(LLMVerseException):
    """Raised when there's a configuration error."""
    pass


class ValidationError(LLMVerseException):
    """Raised when input validation fails."""
    pass


class LLMProviderError(LLMVerseException):
    """Raised when LLM provider (OpenAI) returns an error."""
    pass


class RateLimitError(LLMProviderError):
    """Raised when rate limit is exceeded."""
    pass


class AuthenticationError(LLMProviderError):
    """Raised when authentication fails."""
    pass


class TimeoutError(LLMProviderError):
    """Raised when request times out."""
    pass


class ServiceUnavailableError(LLMProviderError):
    """Raised when service is unavailable."""
    pass
