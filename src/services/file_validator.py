"""File validation service."""

import logging
import mimetypes
from pathlib import Path
from typing import Optional, Tuple
import io

logger = logging.getLogger(__name__)


class FileValidator:
    """Validates uploaded files."""

    # Configuration
    MAX_FILE_SIZE_MB = 50
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
    ALLOWED_EXTENSIONS = {".pdf"}
    ALLOWED_MIME_TYPES = {"application/pdf", "application/x-pdf"}

    @classmethod
    def validate_file(
        cls,
        file_name: str,
        file_size: int,
        file_content: Optional[io.BytesIO] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate uploaded file.

        Args:
            file_name: Name of the file
            file_size: Size of file in bytes
            file_content: Optional file content for deeper validation

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate file extension
        valid, error = cls._validate_extension(file_name)
        if not valid:
            return valid, error

        # Validate file size
        valid, error = cls._validate_size(file_size)
        if not valid:
            return valid, error

        # Validate MIME type if content provided
        if file_content:
            valid, error = cls._validate_mime_type(file_name, file_content)
            if not valid:
                return valid, error

        logger.info(f"File validation passed for: {file_name}")
        return True, None

    @classmethod
    def _validate_extension(cls, file_name: str) -> Tuple[bool, Optional[str]]:
        """Validate file extension."""
        file_path = Path(file_name)
        extension = file_path.suffix.lower()

        if extension not in cls.ALLOWED_EXTENSIONS:
            error_msg = (
                f"Invalid file type. Only PDF files are supported. "
                f"Your file: {extension or 'no extension'}"
            )
            logger.warning(f"Invalid extension: {extension} for file: {file_name}")
            return False, error_msg

        return True, None

    @classmethod
    def _validate_size(cls, file_size: int) -> Tuple[bool, Optional[str]]:
        """Validate file size."""
        if file_size == 0:
            return False, "File is empty (0 bytes)."

        if file_size > cls.MAX_FILE_SIZE_BYTES:
            size_mb = file_size / (1024 * 1024)
            error_msg = (
                f"File too large. Maximum size: {cls.MAX_FILE_SIZE_MB}MB. "
                f"Your file: {size_mb:.2f}MB"
            )
            logger.warning(f"File too large: {size_mb:.2f}MB")
            return False, error_msg

        return True, None

    @classmethod
    def _validate_mime_type(
        cls,
        file_name: str,
        file_content: io.BytesIO
    ) -> Tuple[bool, Optional[str]]:
        """Validate MIME type."""
        # Guess MIME type from extension
        mime_type, _ = mimetypes.guess_type(file_name)

        if mime_type not in cls.ALLOWED_MIME_TYPES:
            # Check file magic bytes for PDF signature
            file_content.seek(0)
            header = file_content.read(4)
            file_content.seek(0)

            # PDF files start with %PDF
            if not header.startswith(b'%PDF'):
                error_msg = (
                    "File does not appear to be a valid PDF. "
                    f"Detected type: {mime_type or 'unknown'}"
                )
                logger.warning(f"Invalid MIME type: {mime_type} for file: {file_name}")
                return False, error_msg

        return True, None

    @classmethod
    def format_file_size(cls, size_bytes: int) -> str:
        """Format file size for display."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.2f} MB"



