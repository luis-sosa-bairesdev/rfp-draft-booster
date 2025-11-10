"""Storage manager for handling file uploads and storage."""

import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional
import io

from models.rfp import RFP

logger = logging.getLogger(__name__)


class StorageManager:
    """Manages file storage for RFP documents."""

    def __init__(self, base_upload_dir: str = "data/uploads"):
        """
        Initialize storage manager.

        Args:
            base_upload_dir: Base directory for uploads
        """
        self.base_upload_dir = Path(base_upload_dir)
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Ensure required directories exist."""
        self.base_upload_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Upload directory ready: {self.base_upload_dir}")

    def save_upload(
        self,
        file_content: io.BytesIO,
        file_name: str,
        rfp_id: str
    ) -> str:
        """
        Save uploaded file to storage.

        Args:
            file_content: File content as BytesIO
            file_name: Original file name
            rfp_id: RFP ID for organizing files

        Returns:
            Path to saved file

        Raises:
            IOError: If save fails
        """
        try:
            # Create subdirectory for this RFP
            rfp_dir = self.base_upload_dir / rfp_id
            rfp_dir.mkdir(parents=True, exist_ok=True)

            # Generate safe filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = f"{timestamp}_{file_name}"
            file_path = rfp_dir / safe_filename

            # Save file
            file_content.seek(0)
            with open(file_path, "wb") as f:
                f.write(file_content.read())

            logger.info(f"Saved file to: {file_path}")
            return str(file_path)

        except Exception as e:
            logger.error(f"Failed to save file: {e}")
            raise IOError(f"Failed to save file: {str(e)}") from e

    def delete_upload(self, file_path: str) -> bool:
        """
        Delete uploaded file.

        Args:
            file_path: Path to file to delete

        Returns:
            True if successful
        """
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                logger.info(f"Deleted file: {file_path}")
                
                # Clean up empty directory
                if path.parent.exists() and not any(path.parent.iterdir()):
                    path.parent.rmdir()
                    logger.info(f"Deleted empty directory: {path.parent}")
                
                return True
            else:
                logger.warning(f"File not found for deletion: {file_path}")
                return False

        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            return False

    def get_file_content(self, file_path: str) -> Optional[bytes]:
        """
        Read file content.

        Args:
            file_path: Path to file

        Returns:
            File content as bytes or None
        """
        try:
            path = Path(file_path)
            if path.exists():
                return path.read_bytes()
            else:
                logger.warning(f"File not found: {file_path}")
                return None

        except Exception as e:
            logger.error(f"Failed to read file: {e}")
            return None

    def cleanup_old_files(self, days: int = 90) -> int:
        """
        Clean up files older than specified days.

        Args:
            days: Age threshold in days

        Returns:
            Number of files deleted
        """
        try:
            deleted_count = 0
            cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)

            for file_path in self.base_upload_dir.rglob("*.pdf"):
                if file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    deleted_count += 1
                    logger.info(f"Cleaned up old file: {file_path}")

            logger.info(f"Cleanup complete. Deleted {deleted_count} files.")
            return deleted_count

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return 0

