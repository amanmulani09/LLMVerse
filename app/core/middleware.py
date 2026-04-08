"""
Middleware for LLMVerse application.

This module provides middleware for request ID tracking, logging,
error handling, and CORS configuration.
"""

import time
import uuid
from typing import Callable
from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add unique request ID to each request."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Add request ID to request state and response headers.
        
        Args:
            request: Incoming request.
            call_next: Next middleware/handler.
            
        Returns:
            Response with request ID header.
        """
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests and responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Log request and response details.
        
        Args:
            request: Incoming request.
            call_next: Next middleware/handler.
            
        Returns:
            Response from handler.
        """
        request_id = getattr(request.state, "request_id", "unknown")
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else "unknown"
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            # Log response
            logger.info(
                f"Request completed: {request.method} {request.url.path} - {response.status_code}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration": f"{duration:.3f}s"
                }
            )
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration": f"{duration:.3f}s",
                    "error": str(e)
                },
                exc_info=True
            )
            raise


def setup_cors(app) -> None:
    """
    Configure CORS middleware.
    
    Args:
        app: FastAPI application instance.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"]
    )
