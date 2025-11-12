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

from services.llm_client import LLMClient, LLMProvider, create_llm_client


class TestLLMClient:
    """Test LLM Client initialization and basic functionality."""
    
    @patch('services.llm_client.genai')
    def test_gemini_initialization(self, mock_genai):
        """Test Gemini client initialization."""
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            client = LLMClient(provider=LLMProvider.GEMINI)
            
            assert client.provider == LLMProvider.GEMINI
            assert client.model == "gemini-pro"
            mock_genai.configure.assert_called_once_with(api_key='test-key')
    
    @patch('services.llm_client.Groq')
    def test_groq_initialization(self, mock_groq_class):
        """Test Groq client initialization."""
        with patch.dict('os.environ', {'GROQ_API_KEY': 'test-key'}):
            client = LLMClient(provider=LLMProvider.GROQ)
            
            assert client.provider == LLMProvider.GROQ
            assert client.model == "mixtral-8x7b-32768"
            mock_groq_class.assert_called_once_with(api_key='test-key')
    
    def test_initialization_without_api_key_raises_error(self):
        """Test that initialization without API key raises error."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="GEMINI_API_KEY not found"):
                LLMClient(provider=LLMProvider.GEMINI)
    
    @patch('services.llm_client.genai')
    def test_custom_model_selection(self, mock_genai):
        """Test custom model can be specified."""
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            client = LLMClient(
                provider=LLMProvider.GEMINI,
                model="custom-model"
            )
            
            assert client.model == "custom-model"
    
    @patch('services.llm_client.genai')
    def test_custom_temperature(self, mock_genai):
        """Test custom temperature can be set."""
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            client = LLMClient(
                provider=LLMProvider.GEMINI,
                temperature=0.5
            )
            
            assert client.temperature == 0.5


class TestLLMGeneration:
    """Test LLM text generation."""
    
    @patch('services.llm_client.genai')
    def test_gemini_generate(self, mock_genai):
        """Test text generation with Gemini."""
        # Mock the response
        mock_response = Mock()
        mock_response.text = "Generated response text"
        
        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            client = LLMClient(provider=LLMProvider.GEMINI)
            result = client.generate("Test prompt")
            
            assert result == "Generated response text"
            mock_model.generate_content.assert_called_once()
    
    @patch('services.llm_client.Groq')
    def test_groq_generate(self, mock_groq_class):
        """Test text generation with Groq."""
        # Mock the response
        mock_choice = Mock()
        mock_choice.message.content = "Generated response from Groq"
        
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_groq_class.return_value = mock_client
        
        with patch.dict('os.environ', {'GROQ_API_KEY': 'test-key'}):
            client = LLMClient(provider=LLMProvider.GROQ)
            result = client.generate("Test prompt")
            
            assert result == "Generated response from Groq"


class TestJSONExtraction:
    """Test JSON extraction from LLM responses."""
    
    @patch('services.llm_client.genai')
    def test_extract_json_from_raw_array(self, mock_genai):
        """Test extracting JSON array from raw text."""
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            client = LLMClient(provider=LLMProvider.GEMINI)
            
            text = '[{"name": "item1"}, {"name": "item2"}]'
            result = client.extract_json(text)
            
            assert len(result) == 2
            assert result[0]["name"] == "item1"
            assert result[1]["name"] == "item2"
    
    @patch('services.llm_client.genai')
    def test_extract_json_from_markdown_code_block(self, mock_genai):
        """Test extracting JSON from markdown code block."""
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            client = LLMClient(provider=LLMProvider.GEMINI)
            
            text = '''Here are the results:
```json
[{"name": "item1"}, {"name": "item2"}]
```
Hope this helps!'''
            
            result = client.extract_json(text)
            
            assert len(result) == 2
            assert result[0]["name"] == "item1"
    
    @patch('services.llm_client.genai')
    def test_extract_json_from_generic_code_block(self, mock_genai):
        """Test extracting JSON from generic code block."""
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            client = LLMClient(provider=LLMProvider.GEMINI)
            
            text = '''```
[{"name": "item1"}]
```'''
            
            result = client.extract_json(text)
            
            assert len(result) == 1
    
    @patch('services.llm_client.genai')
    def test_extract_json_with_surrounding_text(self, mock_genai):
        """Test extracting JSON when surrounded by other text."""
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            client = LLMClient(provider=LLMProvider.GEMINI)
            
            text = 'Some text before [{"name": "item1"}] some text after'
            result = client.extract_json(text)
            
            assert len(result) == 1
    
    @patch('services.llm_client.genai')
    def test_extract_json_single_object_wrapped_in_array(self, mock_genai):
        """Test single JSON object is wrapped in array."""
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            client = LLMClient(provider=LLMProvider.GEMINI)
            
            text = '{"name": "single item"}'
            result = client.extract_json(text)
            
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0]["name"] == "single item"
    
    @patch('services.llm_client.genai')
    def test_extract_json_no_json_raises_error(self, mock_genai):
        """Test error when no JSON found in text."""
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            client = LLMClient(provider=LLMProvider.GEMINI)
            
            with pytest.raises(ValueError, match="No JSON found"):
                client.extract_json("Just some text without JSON")
    
    @patch('services.llm_client.genai')
    def test_extract_json_invalid_json_raises_error(self, mock_genai):
        """Test error when JSON is malformed."""
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            client = LLMClient(provider=LLMProvider.GEMINI)
            
            with pytest.raises(ValueError, match="Invalid JSON"):
                client.extract_json('[{"name": "item1",}]')  # Trailing comma


class TestConnectionTesting:
    """Test connection testing functionality."""
    
    @patch('services.llm_client.genai')
    def test_connection_test_success(self, mock_genai):
        """Test successful connection test."""
        mock_response = Mock()
        mock_response.text = "OK"
        
        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            client = LLMClient(provider=LLMProvider.GEMINI)
            assert client.test_connection() is True
    
    @patch('services.llm_client.genai')
    def test_connection_test_failure(self, mock_genai):
        """Test failed connection test."""
        mock_model = Mock()
        mock_model.generate_content.side_effect = Exception("Connection failed")
        mock_genai.GenerativeModel.return_value = mock_model
        
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            client = LLMClient(provider=LLMProvider.GEMINI)
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
    
    @patch('services.llm_client.LLMClient')
    def test_create_client_with_fallback(self, mock_llm_class):
        """Test fallback to different providers."""
        # First provider fails, second succeeds
        mock_failing = Mock()
        mock_failing.test_connection.return_value = False
        
        mock_working = Mock()
        mock_working.test_connection.return_value = True
        
        mock_llm_class.side_effect = [
            mock_failing,  # Gemini fails
            mock_working,  # Groq works
        ]
        
        client = create_llm_client(fallback=True)
        
        assert client == mock_working
        assert mock_llm_class.call_count == 2
    
    @patch('services.llm_client.LLMClient')
    def test_create_client_all_providers_fail(self, mock_llm_class):
        """Test error when all providers fail."""
        mock_llm_class.side_effect = Exception("Failed")
        
        with pytest.raises(RuntimeError, match="Failed to connect to any LLM provider"):
            create_llm_client(fallback=True)

