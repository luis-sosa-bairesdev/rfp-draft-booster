"""
Tests for LLM Client methods that don't require full initialization.
"""

import pytest
from unittest.mock import Mock
from services.llm_client import LLMClient, LLMProvider


class TestLLMClientMethods:
    """Test LLM client methods that can be tested without full initialization."""
    
    def test_extract_json_static_method(self):
        """Test extract_json as a static method."""
        # Create a minimal client instance
        client = Mock(spec=LLMClient)
        client.extract_json = LLMClient.extract_json.__get__(client, LLMClient)
        
        # Test various JSON extraction scenarios
        text = '[{"name": "item1"}]'
        result = client.extract_json(text)
        assert len(result) == 1
        
        text = '```json\n[{"name": "item1"}]\n```'
        result = client.extract_json(text)
        assert len(result) == 1
        
        text = 'Some text {"name": "item1"} more text'
        result = client.extract_json(text)
        assert len(result) == 1
    
    def test_llm_provider_enum_values(self):
        """Test LLM provider enum."""
        assert LLMProvider.GEMINI == "gemini"
        assert LLMProvider.GROQ == "groq"
        assert LLMProvider.OLLAMA == "ollama"
        
        # Test enum creation
        assert LLMProvider("gemini") == LLMProvider.GEMINI
        assert LLMProvider("groq") == LLMProvider.GROQ
    
    def test_extract_json_with_multiple_code_blocks(self):
        """Test JSON extraction when multiple code blocks exist."""
        client = Mock(spec=LLMClient)
        client.extract_json = LLMClient.extract_json.__get__(client, LLMClient)
        
        text = '''Some text
```python
print("code")
```
```json
[{"name": "item1"}]
```
More text'''
        
        result = client.extract_json(text)
        assert len(result) == 1
    
    def test_extract_json_finds_array_spanning_multiple(self):
        """Test JSON extraction finds array spanning multiple objects."""
        client = Mock(spec=LLMClient)
        client.extract_json = LLMClient.extract_json.__get__(client, LLMClient)
        
        # Text with array that spans from first [ to last ]
        text = 'Text before [{"first": "array"}, {"second": "array"}] text after'
        result = client.extract_json(text)
        # Should extract the complete array
        assert len(result) == 2
    
    def test_extract_json_wraps_single_object(self):
        """Test single object is wrapped in array."""
        client = Mock(spec=LLMClient)
        client.extract_json = LLMClient.extract_json.__get__(client, LLMClient)
        
        text = 'Some text {"name": "single"} more text'
        result = client.extract_json(text)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["name"] == "single"
    
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

