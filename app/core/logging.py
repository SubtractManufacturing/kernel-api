import logging
import sys
from pythonjsonlogger import jsonlogger
from app.core.config import settings

def setup_logging():
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    if settings.LOG_FORMAT == "json":
        logHandler = logging.StreamHandler(sys.stdout)
        formatter = jsonlogger.JsonFormatter(
            fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        logHandler.setFormatter(formatter)
    else:
        logHandler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        logHandler.setFormatter(formatter)
    
    logging.root.setLevel(log_level)
    logging.root.handlers = [logHandler]
    
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with level: {settings.LOG_LEVEL}")
    
    return logger

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)