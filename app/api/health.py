"""
Health check endpoints for LLMVerse application.

This module provides health check endpoints for monitoring
application and dependency status.
"""

from fastapi import APIRouter, Depends
from app.schemas.chat import HealthResponse
from app.core.config import get_settings, Settings
from app.clients.openai_client import get_openai_client, OpenAIClient
from app.core.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check the health status of the application and its dependencies"
)
async def health_check(
    settings: Settings = Depends(get_settings),
    openai_client: OpenAIClient = Depends(get_openai_client)
) -> HealthResponse:
    """
    Comprehensive health check endpoint.
    
    Args:
        settings: Application settings.
        openai_client: OpenAI client for connectivity check.
        
    Returns:
        Health status response with component checks.
    """
    checks = {}
    
    # Check configuration
    try:
        if settings.OPENAI_API_KEY:
            checks["config"] = "healthy"
        else:
            checks["config"] = "unhealthy"
    except Exception as e:
        logger.error(f"Config check failed: {str(e)}")
        checks["config"] = "unhealthy"
    
    # Check OpenAI connectivity (basic check)
    try:
        # Just verify client is initialized
        if openai_client:
            checks["openai_client"] = "healthy"
        else:
            checks["openai_client"] = "unhealthy"
    except Exception as e:
        logger.error(f"OpenAI client check failed: {str(e)}")
        checks["openai_client"] = "unhealthy"
    
    # Determine overall status
    overall_status = "healthy" if all(
        status == "healthy" for status in checks.values()
    ) else "degraded"
    
    return HealthResponse(
        status=overall_status,
        version=settings.APP_VERSION,
        checks=checks
    )


@router.get(
    "/health/ready",
    summary="Readiness check",
    description="Check if the application is ready to serve requests"
)
async def readiness_check() -> dict[str, str]:
    """
    Kubernetes-style readiness probe.
    
    Returns:
        Simple ready status.
    """
    return {"status": "ready"}


@router.get(
    "/health/live",
    summary="Liveness check",
    description="Check if the application is alive"
)
async def liveness_check() -> dict[str, str]:
    """
    Kubernetes-style liveness probe.
    
    Returns:
        Simple alive status.
    """
    return {"status": "alive"}
