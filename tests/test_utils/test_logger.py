"""
Unit tests for logger module.

Tests logger setup, file rotation, and handlers.
"""

import pytest
import logging
import tempfile
import shutil
from pathlib import Path
from src.utils.logger import setup_logger


class TestLoggerSetup:
    """Test logger configuration."""
    
    def test_setup_logger_basic(self):
        """Test basic logger setup."""
        logger = setup_logger(name="test_logger", log_to_file=False, log_to_console=False)
        
        assert logger.name == "test_logger"
        assert logger.level == logging.DEBUG
    
    def test_setup_logger_with_level(self):
        """Test logger with different levels."""
        logger = setup_logger(name="test_info", level="INFO", log_to_file=False, log_to_console=False)
        assert logger.level == logging.INFO
        
        logger = setup_logger(name="test_warning", level="WARNING", log_to_file=False, log_to_console=False)
        assert logger.level == logging.WARNING
    
    def test_logger_file_handler(self):
        """Test that file handler is added when log_to_file=True."""
        logger = setup_logger(name="test_file", log_to_file=True, log_to_console=False)
        
        # Check that at least one handler is a RotatingFileHandler
        from logging.handlers import RotatingFileHandler
        has_file_handler = any(isinstance(h, RotatingFileHandler) for h in logger.handlers)
        assert has_file_handler
    
    def test_logger_console_handler(self):
        """Test that console handler is added when log_to_console=True."""
        logger = setup_logger(name="test_console", log_to_file=False, log_to_console=True)
        
        # Check that at least one handler is a StreamHandler
        has_console_handler = any(isinstance(h, logging.StreamHandler) for h in logger.handlers)
        assert has_console_handler
    
    def test_logger_avoids_duplicate_handlers(self):
        """Test that logger doesn't add duplicate handlers."""
        logger = setup_logger(name="test_unique", log_to_file=False, log_to_console=True)
        handler_count_1 = len(logger.handlers)
        
        # Call setup again
        logger = setup_logger(name="test_unique", log_to_file=False, log_to_console=True)
        handler_count_2 = len(logger.handlers)
        
        assert handler_count_1 == handler_count_2
    
    def test_logger_logs_messages(self, caplog):
        """Test that logger logs messages at different levels."""
        caplog.set_level(logging.DEBUG)
        logger = setup_logger(name="test_messages", log_to_file=False, log_to_console=False)
        
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        
        assert "Debug message" in caplog.text
        assert "Info message" in caplog.text
        assert "Warning message" in caplog.text
        assert "Error message" in caplog.text
    
    def test_logger_formatter(self, caplog):
        """Test that logger uses correct format."""
        caplog.set_level(logging.INFO)
        logger = setup_logger(name="test_format", log_to_file=False, log_to_console=False)
        
        logger.info("Test message")
        
        # Check format contains expected elements
        assert "test_format" in caplog.text
        assert "INFO" in caplog.text
        assert "Test message" in caplog.text


class TestLoggerFileRotation:
    """Test file rotation behavior."""
    
    def test_logs_directory_created(self):
        """Test that logs directory is created."""
        logger = setup_logger(name="test_dir", log_to_file=True, log_to_console=False)
        
        logs_dir = Path("logs")
        assert logs_dir.exists()
        assert logs_dir.is_dir()
    
    def test_log_file_created(self):
        """Test that log file is created."""
        logger = setup_logger(name="test_file_creation", log_to_file=True, log_to_console=False)
        logger.info("Test log entry")
        
        from datetime import datetime
        logs_dir = Path("logs")
        log_file = logs_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
        
        assert log_file.exists()
        assert log_file.is_file()

