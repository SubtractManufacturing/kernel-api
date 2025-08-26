from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import conversion, health, formats
from app.core.config import settings
from app.core.logging import setup_logging
from app.services.file_cleanup import get_cleanup_service
import logging

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    cleanup_service = get_cleanup_service()
    await cleanup_service.start()
    logger.info("File cleanup service started with 30-minute TTL")
    
    yield
    
    # Shutdown
    await cleanup_service.stop()
    logger.info("File cleanup service stopped")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API for converting CAD BREP files to mesh formats using OpenCascade",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(formats.router, prefix="/api/v1", tags=["formats"])
app.include_router(conversion.router, prefix="/api/v1", tags=["conversion"])

@app.get("/")
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": "CAD file conversion API",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }