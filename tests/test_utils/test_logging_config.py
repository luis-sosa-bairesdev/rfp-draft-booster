"""
Tests for logging configuration.
"""

import pytest
import logging
from unittest.mock import patch, MagicMock
from pathlib import Path
from utils.logging_config import setup_logging


class TestLoggingConfig:
    """Test logging configuration."""
    
    @patch('utils.logging_config.logging.basicConfig')
    @patch('utils.logging_config.Path.mkdir')
    def test_setup_logging_configures_logging(self, mock_mkdir, mock_basic_config):
        """Test setup_logging configures logging."""
        setup_logging()
        
        # Should configure logging
        mock_basic_config.assert_called_once()
        # Should create logs directory
        mock_mkdir.assert_called_once()
    
    @patch('utils.logging_config.logging.basicConfig')
    @patch('utils.logging_config.Path.mkdir')
    def test_setup_logging_with_custom_level(self, mock_mkdir, mock_basic_config):
        """Test setup_logging with custom log level."""
        setup_logging(level="INFO")
        
        # Should configure with INFO level
        mock_basic_config.assert_called_once()
        call_args = mock_basic_config.call_args
        assert call_args[1]['level'] == logging.INFO
    
    @patch('utils.logging_config.logging.getLogger')
    @patch('utils.logging_config.logging.basicConfig')
    @patch('utils.logging_config.Path.mkdir')
    def test_setup_logging_suppresses_third_party_logs(self, mock_mkdir, mock_basic_config, mock_get_logger):
        """Test setup_logging suppresses third-party logs."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        setup_logging()
        
        # Should suppress urllib3, google, streamlit logs
        assert mock_get_logger.call_count >= 3

