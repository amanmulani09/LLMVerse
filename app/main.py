"""
LLMVerse - FastAPI application for LLM interactions.

This is the main application module that configures FastAPI,
middleware, error handlers, and routes.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.api.router import router as api_router
from app.core.config import get_settings
from app.core.logging_config import setup_logging, get_logger
from app.core.middleware import (
    RequestIDMiddleware,
    LoggingMiddleware,
    setup_cors
)
from app.clients.openai_client import close_openai_client

# Initialize settings and logging
settings = get_settings()
setup_logging(log_level=settings.LOG_LEVEL)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    
    Args:
        app: FastAPI application instance.
    """
    # Startup
    logger.info(
        f"Starting {settings.APP_NAME} v{settings.APP_VERSION}",
        extra={
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "debug": settings.DEBUG
        }
    )
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    await close_openai_client()
    logger.info("Cleanup completed")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A production-ready FastAPI application for LLM interactions",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Setup CORS
setup_cors(app)

# Add middleware (order matters - they execute in reverse order)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIDMiddleware)


# Custom exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """
    Handle Pydantic validation errors.
    
    Args:
        request: Incoming request.
        exc: Validation exception.
        
    Returns:
        JSON response with validation error details.
    """
    request_id = getattr(request.state, "request_id", None)
    
    logger.warning(
        "Request validation failed",
        extra={
            "request_id": request_id,
            "errors": exc.errors()
        }
    )
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": "Request validation failed",
            "details": exc.errors(),
            "request_id": request_id
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """
    Global exception handler for unhandled exceptions.
    
    Args:
        request: Incoming request.
        exc: Unhandled exception.
        
    Returns:
        JSON response with error details.
    """
    request_id = getattr(request.state, "request_id", None)
    
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={"request_id": request_id},
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": "An unexpected error occurred",
            "request_id": request_id
        }
    )


# Include API router
app.include_router(api_router, prefix="/api/v1")


# Root endpoint
@app.get(
    "/",
    tags=["root"],
    summary="Root endpoint",
    description="Get basic API information"
)
async def root() -> dict[str, str]:
    """
    Root endpoint providing API information.
    
    Returns:
        API information dictionary.
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }
