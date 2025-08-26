import asyncio
import tempfile
import time
from pathlib import Path
import pytest
from app.services.file_cleanup import FileCleanupService


@pytest.mark.asyncio
async def test_file_cleanup_service():
    """Test that the file cleanup service removes expired files."""
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test files
        old_file = temp_path / "old_file.txt"
        new_file = temp_path / "new_file.txt"
        
        # Create old file and modify its timestamp to be older than TTL
        old_file.write_text("old content")
        # Set modification time to 35 minutes ago
        old_time = time.time() - (35 * 60)
        import os
        os.utime(str(old_file), (old_time, old_time))
        
        # Create new file (current timestamp)
        new_file.write_text("new content")
        
        # Create cleanup service with 30-minute TTL
        service = FileCleanupService(
            directories=[str(temp_path)],
            ttl_minutes=30
        )
        
        # Run cleanup
        cleaned = service._clean_directory(temp_path)
        
        # Check results
        assert not old_file.exists(), "Old file should have been deleted"
        assert new_file.exists(), "New file should still exist"
        assert cleaned == 1, "Should have cleaned 1 file"


@pytest.mark.asyncio
async def test_cleanup_service_lifecycle():
    """Test starting and stopping the cleanup service."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        service = FileCleanupService(
            directories=[temp_dir],
            ttl_minutes=30
        )
        
        # Test initial state
        assert not service.running
        
        # Start service
        await service.start()
        assert service.running
        
        # Try to start again (should log warning)
        await service.start()
        assert service.running
        
        # Stop service
        await service.stop()
        assert not service.running
        
        # Stop again (should be safe)
        await service.stop()
        assert not service.running


def test_cleanup_stats():
    """Test getting cleanup service statistics."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        service = FileCleanupService(
            directories=[temp_dir],
            ttl_minutes=30
        )
        
        stats = service.get_stats()
        
        assert stats["running"] == False
        assert stats["ttl_minutes"] == 30
        assert temp_dir in stats["directories"]
        assert stats["cleaned_files_count"] == 0


def test_expired_file_detection():
    """Test detection of expired files."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        test_file = temp_path / "test.txt"
        test_file.write_text("content")
        
        service = FileCleanupService(
            directories=[temp_dir],
            ttl_minutes=30
        )
        
        # File is new, should not be expired
        assert not service._is_file_expired(test_file)
        
        # Modify timestamp to make it old
        old_time = time.time() - (35 * 60)
        import os
        os.utime(str(test_file), (old_time, old_time))
        
        # File should now be expired
        assert service._is_file_expired(test_file)


def test_subdirectory_cleanup():
    """Test that subdirectories are also cleaned."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create subdirectory with files
        sub_dir = temp_path / "subdir"
        sub_dir.mkdir()
        
        old_file = sub_dir / "old.txt"
        old_file.write_text("old")
        
        # Make file old
        old_time = time.time() - (35 * 60)
        import os
        os.utime(str(old_file), (old_time, old_time))
        
        service = FileCleanupService(
            directories=[str(temp_path)],
            ttl_minutes=30
        )
        
        # Clean directory
        cleaned = service._clean_directory(temp_path)
        
        # Check that old file in subdirectory was deleted
        assert not old_file.exists()
        assert cleaned == 1
        
        # Empty subdirectory should also be removed
        assert not sub_dir.exists()


if __name__ == "__main__":
    # Run tests
    import sys
    sys.exit(pytest.main([__file__, "-v"]))