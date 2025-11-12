"""
Simplified tests for LLM Client that don't require complex mocking.

These tests focus on functionality that can be tested without actual API calls.
"""

import pytest
from unittest.mock import Mock, patch
import os

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
        # Create a client instance without initializing the actual client
        # We'll just test the extract_json method which doesn't need the client
        with patch('services.llm_client.genai'), patch('services.llm_client.Groq'):
            try:
                client = LLMClient(provider=LLMProvider.GEMINI, api_key='test-key')
            except:
                # If initialization fails, create a mock client just for extract_json
                client = Mock(spec=LLMClient)
                client.extract_json = LLMClient.extract_json.__get__(client, LLMClient)
            
            text = '[{"name": "item1"}, {"name": "item2"}]'
            result = client.extract_json(text)
            
            assert len(result) == 2
            assert result[0]["name"] == "item1"
            assert result[1]["name"] == "item2"
    
    def test_extract_json_from_markdown(self):
        """Test extracting JSON from markdown code block."""
        with patch('services.llm_client.genai'), patch('services.llm_client.Groq'):
            try:
                client = LLMClient(provider=LLMProvider.GEMINI, api_key='test-key')
            except:
                client = Mock(spec=LLMClient)
                client.extract_json = LLMClient.extract_json.__get__(client, LLMClient)
            
            text = '''```json
[{"name": "item1"}]
```'''
            result = client.extract_json(text)
            assert len(result) == 1
    
    def test_extract_json_single_object(self):
        """Test single JSON object wrapped in array."""
        with patch('services.llm_client.genai'), patch('services.llm_client.Groq'):
            try:
                client = LLMClient(provider=LLMProvider.GEMINI, api_key='test-key')
            except:
                client = Mock(spec=LLMClient)
                client.extract_json = LLMClient.extract_json.__get__(client, LLMClient)
            
            text = '{"name": "single"}'
            result = client.extract_json(text)
            assert isinstance(result, list)
            assert len(result) == 1
    
    def test_extract_json_no_json_raises_error(self):
        """Test error when no JSON found."""
        with patch('services.llm_client.genai'), patch('services.llm_client.Groq'):
            try:
                client = LLMClient(provider=LLMProvider.GEMINI, api_key='test-key')
            except:
                client = Mock(spec=LLMClient)
                client.extract_json = LLMClient.extract_json.__get__(client, LLMClient)
            
            with pytest.raises(ValueError, match="No JSON found"):
                client.extract_json("No JSON here")



