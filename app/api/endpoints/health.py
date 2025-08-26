from fastapi import APIRouter
from app.core.config import settings
from app.services.file_cleanup import get_cleanup_service

router = APIRouter()

@router.get("/health")
async def health_check():
    cleanup_stats = get_cleanup_service().get_stats()
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "opencascade_enabled": settings.ENABLE_OPENCASCADE,
        "file_cleanup": cleanup_stats
    }