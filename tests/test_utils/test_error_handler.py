"""
Comprehensive unit tests for error_handler.py.

Target: Increase coverage from 29% to 80%+
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from utils.error_handler import (
    AppError,
    LLMError,
    ValidationError,
    PDFError,
    SessionError,
    handle_error,
    handle_errors,
    get_error_summary,
    _handle_llm_error_ui,
    _handle_validation_error_ui,
    _handle_pdf_error_ui,
    _handle_session_error_ui
)


# ============================================================================
# Test Custom Exception Classes
# ============================================================================

class TestAppError:
    """Test AppError base exception."""
    
    def test_app_error_basic(self):
        """Test basic AppError initialization."""
        error = AppError("Test error")
        assert error.message == "Test error"
        assert error.user_message == "Test error"
        assert error.context == {}
    
    def test_app_error_with_context(self):
        """Test AppError with context."""
        context = {"user_id": 123, "action": "upload"}
        error = AppError("Test error", context=context)
        assert error.context == context
    
    def test_app_error_with_user_message(self):
        """Test AppError with custom user message."""
        error = AppError(
            "Technical error message",
            user_message="User-friendly message"
        )
        assert error.message == "Technical error message"
        assert error.user_message == "User-friendly message"
    
    def test_app_error_str_without_context(self):
        """Test string representation without context."""
        error = AppError("Simple error")
        assert str(error) == "Simple error"
    
    def test_app_error_str_with_context(self):
        """Test string representation with context."""
        error = AppError("Error", context={"key": "value"})
        assert "Error" in str(error)
        assert "key=value" in str(error)


class TestLLMError:
    """Test LLMError exception."""
    
    def test_llm_error_basic(self):
        """Test basic LLMError initialization."""
        error = LLMError("LLM failed")
        assert error.message == "LLM failed"
        assert error.error_code is None
        assert error.retry_after is None
    
    def test_llm_error_with_code(self):
        """Test LLMError with error code."""
        error = LLMError("Rate limit", error_code="RATE_LIMIT", retry_after=60)
        assert error.error_code == "RATE_LIMIT"
        assert error.retry_after == 60
    
    def test_llm_error_timeout(self):
        """Test LLM timeout error."""
        error = LLMError("Request timeout", error_code="TIMEOUT")
        assert error.error_code == "TIMEOUT"
    
    def test_llm_error_invalid_key(self):
        """Test LLM invalid key error."""
        error = LLMError("Invalid API key", error_code="INVALID_KEY")
        assert error.error_code == "INVALID_KEY"


class TestValidationError:
    """Test ValidationError exception."""
    
    def test_validation_error_basic(self):
        """Test basic ValidationError."""
        error = ValidationError("Invalid input")
        assert error.message == "Invalid input"
        assert error.field is None
        assert error.expected is None
    
    def test_validation_error_with_field(self):
        """Test ValidationError with field."""
        error = ValidationError("Invalid email", field="email", expected="user@domain.com")
        assert error.field == "email"
        assert error.expected == "user@domain.com"


class TestPDFError:
    """Test PDFError exception."""
    
    def test_pdf_error_basic(self):
        """Test basic PDFError."""
        error = PDFError("Cannot parse PDF")
        assert error.message == "Cannot parse PDF"
        assert error.pdf_path is None
    
    def test_pdf_error_with_path(self):
        """Test PDFError with file path."""
        error = PDFError("Corrupted PDF", pdf_path="/path/to/file.pdf")
        assert error.pdf_path == "/path/to/file.pdf"


class TestSessionError:
    """Test SessionError exception."""
    
    def test_session_error_basic(self):
        """Test basic SessionError."""
        error = SessionError("Session expired")
        assert error.message == "Session expired"
        assert error.missing_key is None
    
    def test_session_error_with_missing_key(self):
        """Test SessionError with missing key."""
        error = SessionError("Missing RFP", missing_key="rfp")
        assert error.missing_key == "rfp"


# ============================================================================
# Test Error Handler Functions
# ============================================================================

class TestHandleError:
    """Test handle_error function."""
    
    def test_handle_error_basic(self):
        """Test basic error handling."""
        error = AppError("Test error")
        result = handle_error(error, show_ui_error=False)
        assert result is None
    
    def test_handle_error_with_fallback(self):
        """Test error handling with fallback data."""
        error = AppError("Test error")
        fallback = ["mock", "data"]
        result = handle_error(error, fallback_data=fallback, show_ui_error=False)
        assert result == fallback
    
    def test_handle_error_with_context(self):
        """Test error handling with context."""
        error = AppError("Test error")
        context = {"user_id": 123}
        result = handle_error(error, context=context, show_ui_error=False)
        assert result is None
    
    @patch('streamlit.error')
    def test_handle_error_shows_ui(self, mock_st_error):
        """Test that UI error is shown."""
        error = Exception("Generic error")
        handle_error(error, show_ui_error=True, allow_retry=False)
        mock_st_error.assert_called_once()


class TestHandleErrorsDecorator:
    """Test handle_errors decorator."""
    
    def test_decorator_normal_execution(self):
        """Test decorator with successful function execution."""
        @handle_errors(fallback_data=None, show_ui=False)
        def successful_function():
            return "success"
        
        result = successful_function()
        assert result == "success"
    
    def test_decorator_catches_exception(self):
        """Test decorator catches and handles exception."""
        @handle_errors(fallback_data="fallback", show_ui=False)
        def failing_function():
            raise ValueError("Something went wrong")
        
        result = failing_function()
        assert result == "fallback"
    
    def test_decorator_with_args(self):
        """Test decorator with function arguments."""
        @handle_errors(fallback_data=0, show_ui=False)
        def add_numbers(a, b):
            return a + b
        
        result = add_numbers(2, 3)
        assert result == 5
    
    def test_decorator_with_exception_and_args(self):
        """Test decorator catches exception with args."""
        @handle_errors(fallback_data=-1, show_ui=False)
        def divide(a, b):
            return a / b
        
        result = divide(10, 0)  # Division by zero
        assert result == -1


# ============================================================================
# Test UI Handler Functions
# ============================================================================

class TestHandleLLMErrorUI:
    """Test _handle_llm_error_ui function."""
    
    @patch('streamlit.warning')
    def test_rate_limit_error(self, mock_warning):
        """Test rate limit error UI."""
        error = LLMError("Rate limit", error_code="RATE_LIMIT", retry_after=60)
        _handle_llm_error_ui(error, allow_retry=False)
        mock_warning.assert_called_once()
        call_args = str(mock_warning.call_args)
        assert "Rate Limit" in call_args
    
    @patch('streamlit.error')
    def test_timeout_error(self, mock_error):
        """Test timeout error UI."""
        error = LLMError("Timeout", error_code="TIMEOUT")
        _handle_llm_error_ui(error, allow_retry=False)
        mock_error.assert_called_once()
        call_args = str(mock_error.call_args)
        assert "Timed Out" in call_args
    
    @patch('streamlit.error')
    def test_invalid_key_error(self, mock_error):
        """Test invalid key error UI."""
        error = LLMError("Invalid key", error_code="INVALID_KEY")
        _handle_llm_error_ui(error, allow_retry=False)
        mock_error.assert_called_once()
        call_args = str(mock_error.call_args)
        assert "Invalid API Key" in call_args
    
    @patch('streamlit.warning')
    def test_empty_response_error(self, mock_warning):
        """Test empty response error UI."""
        error = LLMError("Empty", error_code="EMPTY_RESPONSE")
        _handle_llm_error_ui(error, allow_retry=False)
        mock_warning.assert_called_once()
    
    @patch('streamlit.error')
    def test_generic_llm_error(self, mock_error):
        """Test generic LLM error UI."""
        error = LLMError("Unknown error", user_message="Something went wrong")
        _handle_llm_error_ui(error, allow_retry=False)
        mock_error.assert_called_once()


class TestHandleValidationErrorUI:
    """Test _handle_validation_error_ui function."""
    
    @patch('streamlit.error')
    def test_validation_error_basic(self, mock_error):
        """Test basic validation error UI."""
        error = ValidationError("Invalid input")
        _handle_validation_error_ui(error)
        mock_error.assert_called_once()
    
    @patch('streamlit.error')
    def test_validation_error_with_field(self, mock_error):
        """Test validation error with field UI."""
        error = ValidationError(
            "Invalid email",
            field="email",
            expected="user@domain.com"
        )
        _handle_validation_error_ui(error)
        mock_error.assert_called_once()
        call_args = str(mock_error.call_args)
        assert "email" in call_args.lower()


class TestHandlePDFErrorUI:
    """Test _handle_pdf_error_ui function."""
    
    @patch('streamlit.error')
    def test_pdf_error_basic(self, mock_error):
        """Test basic PDF error UI."""
        error = PDFError("Cannot parse PDF")
        _handle_pdf_error_ui(error)
        mock_error.assert_called_once()
    
    @patch('streamlit.error')
    def test_pdf_error_with_path(self, mock_error):
        """Test PDF error with path UI."""
        error = PDFError("Corrupted PDF", pdf_path="/path/to/file.pdf")
        _handle_pdf_error_ui(error)
        mock_error.assert_called_once()
        call_args = str(mock_error.call_args)
        assert "file.pdf" in call_args


class TestHandleSessionErrorUI:
    """Test _handle_session_error_ui function."""
    
    @patch('streamlit.warning')
    def test_session_error_basic(self, mock_warning):
        """Test basic session error UI."""
        error = SessionError("Session expired")
        _handle_session_error_ui(error)
        mock_warning.assert_called_once()
    
    @patch('streamlit.warning')
    @patch('streamlit.info')
    def test_session_error_missing_rfp(self, mock_info, mock_warning):
        """Test session error for missing RFP."""
        error = SessionError("No RFP loaded", missing_key="rfp")
        _handle_session_error_ui(error)
        mock_warning.assert_called_once()
        mock_info.assert_called_once()


# ============================================================================
# Test Utility Functions
# ============================================================================

class TestGetErrorSummary:
    """Test get_error_summary function."""
    
    def test_summary_generic_exception(self):
        """Test summary for generic exception."""
        error = ValueError("Test error")
        summary = get_error_summary(error)
        assert summary["type"] == "ValueError"
        assert summary["message"] == "Test error"
    
    def test_summary_app_error(self):
        """Test summary for AppError."""
        error = AppError("App error", context={"key": "value"})
        summary = get_error_summary(error)
        assert summary["type"] == "AppError"
        assert summary["user_message"] == "App error"
        assert summary["context"] == {"key": "value"}
    
    def test_summary_llm_error(self):
        """Test summary for LLMError."""
        error = LLMError("LLM error", error_code="TIMEOUT", retry_after=30)
        summary = get_error_summary(error)
        assert summary["error_code"] == "TIMEOUT"
        assert summary["retry_after"] == 30
    
    def test_summary_validation_error(self):
        """Test summary for ValidationError."""
        error = ValidationError("Invalid", field="email", expected="valid@email.com")
        summary = get_error_summary(error)
        assert summary["field"] == "email"
        assert summary["expected"] == "valid@email.com"
    
    def test_summary_pdf_error(self):
        """Test summary for PDFError."""
        error = PDFError("PDF error", pdf_path="/path/to/file.pdf")
        summary = get_error_summary(error)
        assert summary["pdf_path"] == "/path/to/file.pdf"
    
    def test_summary_session_error(self):
        """Test summary for SessionError."""
        error = SessionError("Session error", missing_key="rfp")
        summary = get_error_summary(error)
        assert summary["missing_key"] == "rfp"
