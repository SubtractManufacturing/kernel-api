import asyncio
import os
import time
import logging
from pathlib import Path
from typing import List, Set
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class FileCleanupService:
    """Service to clean up old temporary files with TTL."""
    
    def __init__(self, directories: List[str], ttl_minutes: int = 30):
        """
        Initialize the file cleanup service.
        
        Args:
            directories: List of directory paths to monitor
            ttl_minutes: Time to live in minutes (default: 30)
        """
        self.directories = [Path(d) for d in directories]
        self.ttl_seconds = ttl_minutes * 60
        self.running = False
        self._task = None
        self._cleaned_files: Set[str] = set()
        
    def _is_file_expired(self, file_path: Path) -> bool:
        """Check if a file has exceeded its TTL."""
        try:
            file_age = time.time() - file_path.stat().st_mtime
            return file_age > self.ttl_seconds
        except (OSError, IOError):
            return False
    
    def _clean_directory(self, directory: Path) -> int:
        """Clean expired files from a directory."""
        if not directory.exists():
            return 0
        
        cleaned_count = 0
        try:
            for item in directory.iterdir():
                if item.is_file():
                    file_key = str(item.absolute())
                    if self._is_file_expired(item) and file_key not in self._cleaned_files:
                        try:
                            item.unlink()
                            self._cleaned_files.add(file_key)
                            cleaned_count += 1
                            logger.info(f"Cleaned up expired file: {item.name}")
                        except (OSError, IOError) as e:
                            logger.warning(f"Failed to delete {item}: {e}")
                elif item.is_dir() and item.name not in ['.', '..']:
                    # Recursively clean subdirectories
                    cleaned_count += self._clean_directory(item)
                    # Try to remove empty directories
                    try:
                        if not any(item.iterdir()):
                            item.rmdir()
                            logger.info(f"Removed empty directory: {item.name}")
                    except (OSError, IOError):
                        pass
        except (OSError, IOError) as e:
            logger.error(f"Error cleaning directory {directory}: {e}")
        
        return cleaned_count
    
    async def _cleanup_loop(self):
        """Main cleanup loop that runs periodically."""
        logger.info(f"File cleanup service started with TTL of {self.ttl_seconds/60:.0f} minutes")
        
        while self.running:
            try:
                total_cleaned = 0
                for directory in self.directories:
                    if directory.exists():
                        cleaned = self._clean_directory(directory)
                        total_cleaned += cleaned
                
                if total_cleaned > 0:
                    logger.info(f"Cleanup cycle completed: {total_cleaned} files removed")
                
                # Clean up the set of cleaned files periodically
                current_time = time.time()
                self._cleaned_files = {
                    f for f in self._cleaned_files 
                    if Path(f).exists() and not self._is_file_expired(Path(f))
                }
                
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
            
            # Wait 5 minutes before next cleanup cycle
            await asyncio.sleep(300)
    
    async def start(self):
        """Start the cleanup service."""
        if self.running:
            logger.warning("Cleanup service is already running")
            return
        
        self.running = True
        self._task = asyncio.create_task(self._cleanup_loop())
        logger.info("File cleanup service started")
    
    async def stop(self):
        """Stop the cleanup service."""
        if not self.running:
            return
        
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("File cleanup service stopped")
    
    def get_stats(self) -> dict:
        """Get statistics about the cleanup service."""
        stats = {
            "running": self.running,
            "ttl_minutes": self.ttl_seconds / 60,
            "directories": [str(d) for d in self.directories],
            "cleaned_files_count": len(self._cleaned_files)
        }
        
        # Add directory sizes
        for directory in self.directories:
            if directory.exists():
                try:
                    file_count = sum(1 for _ in directory.rglob("*") if _.is_file())
                    stats[f"{directory.name}_file_count"] = file_count
                except (OSError, IOError):
                    stats[f"{directory.name}_file_count"] = "error"
        
        return stats


# Global instance
cleanup_service = None


def get_cleanup_service() -> FileCleanupService:
    """Get the global cleanup service instance."""
    global cleanup_service
    if cleanup_service is None:
        from app.core.config import settings
        
        directories = [
            settings.UPLOAD_DIR,
            settings.OUTPUT_DIR,
            "temp"
        ]
        
        cleanup_service = FileCleanupService(
            directories=directories,
            ttl_minutes=30
        )
    
    return cleanup_service