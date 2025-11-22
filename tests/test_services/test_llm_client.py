"""
Unit tests for LLM Client.

Tests cover:
- Client initialization for different providers
- API key handling
- Text generation with mocked responses
- JSON extraction from various formats
- Error handling and fallback logic
- Connection testing
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import os
import sys

from services.llm_client import LLMClient, LLMProvider, create_llm_client
from src.utils.error_handler import LLMError


class TestLLMClient:
    """Test LLM Client initialization and basic functionality."""
    
    def test_gemini_initialization(self):
        """Test Gemini client initialization."""
        mock_genai = MagicMock()
        mock_model_instance = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model_instance
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            with patch.dict('sys.modules', {'google.generativeai': mock_genai}):
                client = LLMClient(provider=LLMProvider.GEMINI, api_key='test-key')
                
                assert client.provider == LLMProvider.GEMINI
                assert client.model == "gemini-2.5-flash"  # Default model updated
                assert client._client is not None
    
    def test_groq_initialization(self):
        """Test Groq client initialization."""
        mock_groq_module = MagicMock()
        mock_groq_instance = MagicMock()
        mock_groq_module.Groq.return_value = mock_groq_instance
        
        with patch.dict(os.environ, {'GROQ_API_KEY': 'test-key'}):
            with patch.dict('sys.modules', {'groq': mock_groq_module}):
                client = LLMClient(provider=LLMProvider.GROQ, api_key='test-key')
                
                assert client.provider == LLMProvider.GROQ
                assert client.model == "mixtral-8x7b-32768"
                assert client._client is not None
    
    def test_initialization_without_api_key_raises_error(self):
        """Test that initialization without API key raises error."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(LLMError, match="GEMINI_API_KEY not found"):
                LLMClient(provider=LLMProvider.GEMINI)
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_custom_model_selection(self, mock_model_class, mock_configure):
        """Test custom model can be specified."""
        mock_model_instance = Mock()
        mock_model_class.return_value = mock_model_instance
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            client = LLMClient(
                provider=LLMProvider.GEMINI,
                api_key='test-key',
                model="custom-model"
            )
            
            assert client.model == "custom-model"
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_custom_temperature(self, mock_model_class, mock_configure):
        """Test custom temperature can be set."""
        mock_model_instance = Mock()
        mock_model_class.return_value = mock_model_instance
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            client = LLMClient(
                provider=LLMProvider.GEMINI,
                api_key='test-key',
                temperature=0.5
            )
            
            assert client.temperature == 0.5


class TestLLMGeneration:
    """Test LLM text generation."""
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_gemini_generate(self, mock_model_class, mock_configure):
        """Test text generation with Gemini."""
        # Mock the response
        mock_response = Mock()
        mock_response.text = "Generated response text"
        
        mock_model_instance = Mock()
        mock_model_instance.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model_instance
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            client = LLMClient(provider=LLMProvider.GEMINI, api_key='test-key')
            result = client.generate("Test prompt")
            
            assert result == "Generated response text"
            mock_model_instance.generate_content.assert_called_once()
    
    def test_groq_generate(self):
        """Test text generation with Groq."""
        # Mock the response
        mock_choice = MagicMock()
        mock_choice.message.content = "Generated response from Groq"
        
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        
        mock_groq_instance = MagicMock()
        mock_groq_instance.chat.completions.create.return_value = mock_response
        
        mock_groq_module = MagicMock()
        mock_groq_module.Groq.return_value = mock_groq_instance
        
        with patch.dict(os.environ, {'GROQ_API_KEY': 'test-key'}):
            with patch.dict('sys.modules', {'groq': mock_groq_module}):
                client = LLMClient(provider=LLMProvider.GROQ, api_key='test-key')
                result = client.generate("Test prompt")
                
                assert result == "Generated response from Groq"


class TestJSONExtraction:
    """Test JSON extraction from LLM responses."""
    
    def _create_client_for_json_test(self):
        """Helper to create client just for JSON extraction tests."""
        # Create a minimal client instance without full initialization
        client = Mock(spec=LLMClient)
        # Bind the extract_json method to the mock
        client.extract_json = LLMClient.extract_json.__get__(client, LLMClient)
        return client
    
    def test_extract_json_from_raw_array(self):
        """Test extracting JSON array from raw text."""
        client = self._create_client_for_json_test()
        
        text = '[{"name": "item1"}, {"name": "item2"}]'
        result = client.extract_json(text)
        
        assert len(result) == 2
        assert result[0]["name"] == "item1"
        assert result[1]["name"] == "item2"
    
    def test_extract_json_from_markdown_code_block(self):
        """Test extracting JSON from markdown code block."""
        client = self._create_client_for_json_test()
        
        text = '''Here are the results:
```json
[{"name": "item1"}, {"name": "item2"}]
```
Hope this helps!'''
        
        result = client.extract_json(text)
        
        assert len(result) == 2
        assert result[0]["name"] == "item1"
    
    def test_extract_json_from_generic_code_block(self):
        """Test extracting JSON from generic code block."""
        client = self._create_client_for_json_test()
        
        text = '''```
[{"name": "item1"}]
```'''
        
        result = client.extract_json(text)
        
        assert len(result) == 1
    
    def test_extract_json_with_surrounding_text(self):
        """Test extracting JSON when surrounded by other text."""
        client = self._create_client_for_json_test()
        
        text = 'Some text before [{"name": "item1"}] some text after'
        result = client.extract_json(text)
        
        assert len(result) == 1
    
    def test_extract_json_single_object_wrapped_in_array(self):
        """Test single JSON object is wrapped in array."""
        client = self._create_client_for_json_test()
        
        text = '{"name": "single item"}'
        result = client.extract_json(text)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["name"] == "single item"
    
    def test_extract_json_no_json_raises_error(self):
        """Test error when no JSON found in text."""
        client = self._create_client_for_json_test()
        
        with pytest.raises(ValueError, match="No JSON found"):
            client.extract_json("Just some text without JSON")
    
    def test_extract_json_invalid_json_raises_error(self):
        """Test error when JSON is malformed."""
        client = self._create_client_for_json_test()
        
        with pytest.raises(ValueError, match="Invalid JSON"):
            client.extract_json('[{"name": "item1",}]')  # Trailing comma


class TestConnectionTesting:
    """Test connection testing functionality."""
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_connection_test_success(self, mock_model_class, mock_configure):
        """Test successful connection test."""
        mock_response = Mock()
        mock_response.text = "OK"
        
        mock_model_instance = Mock()
        mock_model_instance.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model_instance
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            client = LLMClient(provider=LLMProvider.GEMINI, api_key='test-key')
            assert client.test_connection() is True
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_connection_test_failure(self, mock_model_class, mock_configure):
        """Test failed connection test."""
        mock_model_instance = Mock()
        mock_model_instance.generate_content.side_effect = Exception("Connection failed")
        mock_model_class.return_value = mock_model_instance
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            client = LLMClient(provider=LLMProvider.GEMINI, api_key='test-key')
            assert client.test_connection() is False


class TestClientFactory:
    """Test create_llm_client factory function."""
    
    @patch('services.llm_client.LLMClient')
    def test_create_client_with_provider(self, mock_llm_class):
        """Test creating client with specific provider."""
        mock_instance = Mock()
        mock_instance.test_connection.return_value = True
        mock_llm_class.return_value = mock_instance
        
        client = create_llm_client(provider="gemini", fallback=False)
        
        mock_llm_class.assert_called_once()
        assert client == mock_instance
    
    @patch('services.llm_client._is_provider_available')
    @patch('services.llm_client.LLMClient.test_connection')
    def test_create_client_with_fallback(self, mock_test_conn, mock_is_available):
        """Test fallback to different providers."""
        # Mock provider availability: Gemini not available, Groq available
        def side_effect(provider):
            if provider == LLMProvider.GEMINI:
                return (False, "Gemini not available")
            elif provider == LLMProvider.GROQ:
                return (True, None)
            else:
                return (False, "Not available")
        
        mock_is_available.side_effect = side_effect
        mock_test_conn.return_value = True  # Mock successful connection test
        
        mock_groq = MagicMock()
        mock_groq_instance = MagicMock()
        mock_groq.Groq.return_value = mock_groq_instance
        
        with patch.dict(os.environ, {'GROQ_API_KEY': 'test-key'}):
            with patch.dict('sys.modules', {'groq': mock_groq}):
                client = create_llm_client(fallback=True)
                
                # Should use Groq since Gemini is not available
                assert client is not None
                assert client.provider == LLMProvider.GROQ
    
    @patch('services.llm_client.LLMClient')
    def test_create_client_all_providers_fail(self, mock_llm_class):
        """Test error when all providers fail."""
        mock_llm_class.side_effect = Exception("Failed")
        
        with pytest.raises(RuntimeError, match="Failed to connect to any LLM provider"):
            create_llm_client(fallback=True)
