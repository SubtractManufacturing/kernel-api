from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Kernel API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    UPLOAD_DIR: str = "uploads"
    OUTPUT_DIR: str = "outputs"
    TEMP_DIR: str = "temp"
    
    SUPPORTED_INPUT_FORMATS: List[str] = ["step", "stp", "iges", "igs", "brep"]
    SUPPORTED_OUTPUT_FORMATS: List[str] = ["stl", "obj", "glb", "gltf"]
    
    DEFAULT_DEFLECTION: float = 0.1
    DEFAULT_ANGULAR_DEFLECTION: float = 0.5
    
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    ENABLE_OPENCASCADE: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
os.makedirs(settings.TEMP_DIR, exist_ok=True)