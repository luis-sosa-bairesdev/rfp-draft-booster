"""
Tests for LLM Client helper methods that don't require full initialization.
"""

import pytest
from unittest.mock import Mock, patch
from services.llm_client import LLMClient, LLMProvider


class TestLLMClientHelpers:
    """Test LLM client helper methods."""
    
    def test_llm_provider_default_models(self):
        """Test default models for each provider."""
        # Test default models mapping
        defaults = {
            LLMProvider.GEMINI: "gemini-pro",
            LLMProvider.GROQ: "mixtral-8x7b-32768",
            LLMProvider.OLLAMA: "llama2",
        }
        
        assert defaults[LLMProvider.GEMINI] == "gemini-pro"
        assert defaults[LLMProvider.GROQ] == "mixtral-8x7b-32768"
        assert defaults[LLMProvider.OLLAMA] == "llama2"
    
    def test_extract_json_edge_cases(self):
        """Test JSON extraction edge cases."""
        client = Mock(spec=LLMClient)
        client.extract_json = LLMClient.extract_json.__get__(client, LLMClient)
        
        # Test with whitespace
        text = '   [{"name": "item1"}]   '
        result = client.extract_json(text)
        assert len(result) == 1
        
        # Test with newlines
        text = '\n\n[{"name": "item1"}]\n\n'
        result = client.extract_json(text)
        assert len(result) == 1
        
        # Test nested JSON
        text = '[{"name": "item1", "data": {"nested": "value"}}]'
        result = client.extract_json(text)
        assert len(result) == 1
        assert result[0]["data"]["nested"] == "value"

