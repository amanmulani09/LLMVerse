"""
API router configuration for LLMVerse application.

This module aggregates all API routers and configures
the main API router with proper tags and prefixes.
"""

from fastapi import APIRouter
from app.api.chat import router as chat_router
from app.api.health import router as health_router

# Create main API router
router = APIRouter()

# Include sub-routers with tags
router.include_router(
    chat_router,
    tags=["chat"],
    prefix=""
)

router.include_router(
    health_router,
    tags=["health"],
    prefix=""
)
