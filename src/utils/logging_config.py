"""Logging configuration for RFP Draft Booster."""

import logging
import sys
from pathlib import Path
from src.config import settings


def setup_logging(level: str = None) -> None:
    """Configure application logging.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR). Defaults to DEBUG per BairesDev standards
    """
    # Default to DEBUG level as per BairesDev standards
    log_level = level or settings.log_level or "DEBUG"
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(logs_dir / "app.log"),
        ]
    )
    
    # Suppress verbose third-party logs
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)
    logging.getLogger("streamlit").setLevel(logging.WARNING)
    
    # Log initialization
    logger = logging.getLogger(__name__)
    logger.info(f"{settings.app_name} v{settings.version} - Logging initialized")

