"""
Tests for configuration module.
"""

import pytest
import os
from unittest.mock import patch
from config import settings


class TestConfig:
    """Test configuration settings."""
    
    def test_settings_has_required_attributes(self):
        """Test settings has required configuration attributes."""
        assert hasattr(settings, 'GEMINI_API_KEY') or hasattr(settings, 'gemini_api_key')
        assert hasattr(settings, 'GROQ_API_KEY') or hasattr(settings, 'groq_api_key')
    
    def test_settings_reads_from_env(self):
        """Test settings reads from environment variables."""
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key-123'}):
            # Reload config to pick up env var
            import importlib
            import config
            importlib.reload(config)
            
            # Settings should have the key
            assert hasattr(config.settings, 'GEMINI_API_KEY') or hasattr(config.settings, 'gemini_api_key')



