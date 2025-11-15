"""
Simplified tests for LLM Client that don't require complex mocking.

These tests focus on functionality that can be tested without actual API calls.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
import sys

from services.llm_client import LLMClient, LLMProvider


class TestLLMClientSimple:
    """Simplified LLM client tests."""
    
    def test_llm_provider_enum(self):
        """Test LLM provider enum values."""
        assert LLMProvider.GEMINI.value == "gemini"
        assert LLMProvider.GROQ.value == "groq"
        assert LLMProvider.OLLAMA.value == "ollama"
    
    def test_extract_json_from_raw_array(self):
        """Test extracting JSON array from raw text."""
        mock_genai = MagicMock()
        mock_genai.GenerativeModel.return_value = MagicMock()
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            with patch.dict('sys.modules', {'google.generativeai': mock_genai}):
                client = LLMClient(provider=LLMProvider.GEMINI, api_key='test-key')
                
                text = '[{"name": "item1"}, {"name": "item2"}]'
                result = client.extract_json(text)
                
                assert len(result) == 2
                assert result[0]["name"] == "item1"
                assert result[1]["name"] == "item2"
    
    def test_extract_json_from_markdown(self):
        """Test extracting JSON from markdown code block."""
        mock_genai = MagicMock()
        mock_genai.GenerativeModel.return_value = MagicMock()
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            with patch.dict('sys.modules', {'google.generativeai': mock_genai}):
                client = LLMClient(provider=LLMProvider.GEMINI, api_key='test-key')
                
                text = '''```json
[{"name": "item1"}]
```'''
                result = client.extract_json(text)
                assert len(result) == 1
    
    def test_extract_json_single_object(self):
        """Test single JSON object wrapped in array."""
        mock_genai = MagicMock()
        mock_genai.GenerativeModel.return_value = MagicMock()
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            with patch.dict('sys.modules', {'google.generativeai': mock_genai}):
                client = LLMClient(provider=LLMProvider.GEMINI, api_key='test-key')
                
                text = '{"name": "single"}'
                result = client.extract_json(text)
                assert isinstance(result, list)
                assert len(result) == 1
    
    def test_extract_json_no_json_raises_error(self):
        """Test error when no JSON found."""
        mock_genai = MagicMock()
        mock_genai.GenerativeModel.return_value = MagicMock()
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            with patch.dict('sys.modules', {'google.generativeai': mock_genai}):
                client = LLMClient(provider=LLMProvider.GEMINI, api_key='test-key')
                
                with pytest.raises(ValueError, match="No JSON found"):
                    client.extract_json("No JSON here")



