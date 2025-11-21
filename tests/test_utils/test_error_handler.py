"""
Unit tests for error handler module.

Tests custom exception classes, error handling functions, and decorators.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.utils.error_handler import (
    AppError,
    LLMError,
    ValidationError,
    PDFError,
    SessionError,
    handle_error,
    handle_errors,
    get_error_summary
)


class TestCustomExceptions:
    """Test custom exception classes."""
    
    def test_app_error_basic(self):
        """Test basic AppError creation."""
        error = AppError("Test error")
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.user_message == "Test error"
        assert error.context == {}
    
    def test_app_error_with_context(self):
        """Test AppError with context."""
        context = {"file": "test.pdf", "line": 42}
        error = AppError("Test error", context=context)
        assert error.context == context
        assert "file=test.pdf" in str(error)
        assert "line=42" in str(error)
    
    def test_app_error_with_user_message(self):
        """Test AppError with custom user message."""
        error = AppError(
            "Technical error details",
            user_message="User-friendly message"
        )
        assert error.message == "Technical error details"
        assert error.user_message == "User-friendly message"
    
    def test_llm_error_basic(self):
        """Test basic LLMError creation."""
        error = LLMError("API timeout")
        assert str(error) == "API timeout"
        assert error.error_code is None
        assert error.retry_after is None
    
    def test_llm_error_with_code(self):
        """Test LLMError with error code."""
        error = LLMError(
            "Rate limit exceeded",
            error_code="RATE_LIMIT",
            retry_after=60
        )
        assert error.error_code == "RATE_LIMIT"
        assert error.retry_after == 60
    
    def test_llm_error_timeout(self):
        """Test LLMError timeout scenario."""
        error = LLMError(
            "Request timed out",
            error_code="TIMEOUT",
            user_message="The request took too long"
        )
        assert error.error_code == "TIMEOUT"
        assert error.user_message == "The request took too long"
    
    def test_llm_error_invalid_key(self):
        """Test LLMError invalid key scenario."""
        error = LLMError(
            "401 Unauthorized",
            error_code="INVALID_KEY",
            user_message="API key is invalid"
        )
        assert error.error_code == "INVALID_KEY"
    
    def test_validation_error_basic(self):
        """Test basic ValidationError creation."""
        error = ValidationError("Invalid input")
        assert str(error) == "Invalid input"
        assert error.field is None
        assert error.expected is None
    
    def test_validation_error_with_field(self):
        """Test ValidationError with field and expected."""
        error = ValidationError(
            "Invalid email format",
            field="email",
            expected="user@example.com"
        )
        assert error.field == "email"
        assert error.expected == "user@example.com"
    
    def test_pdf_error_basic(self):
        """Test basic PDFError creation."""
        error = PDFError("Failed to parse PDF")
        assert str(error) == "Failed to parse PDF"
        assert error.pdf_path is None
    
    def test_pdf_error_with_path(self):
        """Test PDFError with file path."""
        error = PDFError(
            "Empty PDF file",
            pdf_path="/path/to/file.pdf"
        )
        assert error.pdf_path == "/path/to/file.pdf"
    
    def test_session_error_basic(self):
        """Test basic SessionError creation."""
        error = SessionError("Missing RFP data")
        assert str(error) == "Missing RFP data"
        assert error.missing_key is None
    
    def test_session_error_with_key(self):
        """Test SessionError with missing key."""
        error = SessionError(
            "RFP not found in session",
            missing_key="rfp"
        )
        assert error.missing_key == "rfp"


class TestHandleError:
    """Test handle_error function."""
    
    def test_handle_error_logs_error(self, caplog):
        """Test that handle_error logs the error."""
        import logging
        caplog.set_level(logging.ERROR)
        
        error = AppError("Test error")
        result = handle_error(error, show_ui_error=False)
        
        assert "AppError" in caplog.text
        assert "Test error" in caplog.text
        assert result is None
    
    def test_handle_error_with_context(self, caplog):
        """Test handle_error with context."""
        import logging
        caplog.set_level(logging.ERROR)
        
        error = AppError("Test error")
        context = {"function": "test_func", "user": "test_user"}
        handle_error(error, context=context, show_ui_error=False)
        
        assert "Test error" in caplog.text
    
    def test_handle_error_returns_fallback(self):
        """Test that handle_error returns fallback data."""
        error = AppError("Test error")
        fallback = {"default": "value"}
        
        result = handle_error(error, fallback_data=fallback, show_ui_error=False)
        
        assert result == fallback
    
    def test_handle_error_without_ui(self):
        """Test handle_error without UI display."""
        error = LLMError("API error", error_code="TIMEOUT")
        result = handle_error(error, show_ui_error=False)
        
        assert result is None
    
    def test_handle_error_with_llm_error_ui(self):
        """Test UI feedback for LLMError doesn't crash."""
        error = LLMError("Timeout", error_code="TIMEOUT")
        # Just verify it doesn't crash - UI testing requires Streamlit environment
        result = handle_error(error, show_ui_error=False, allow_retry=False)
        assert result is None
    
    def test_handle_error_with_validation_error_ui(self):
        """Test UI feedback for ValidationError doesn't crash."""
        error = ValidationError(
            "Invalid email",
            field="email",
            expected="user@example.com"
        )
        # Just verify it doesn't crash - UI testing requires Streamlit environment
        result = handle_error(error, show_ui_error=False)
        assert result is None
    
    def test_handle_error_with_pdf_error_ui(self):
        """Test UI feedback for PDFError doesn't crash."""
        error = PDFError("Empty PDF", pdf_path="test.pdf")
        # Just verify it doesn't crash - UI testing requires Streamlit environment
        result = handle_error(error, show_ui_error=False)
        assert result is None
    
    def test_handle_error_with_session_error_ui(self):
        """Test UI feedback for SessionError doesn't crash."""
        error = SessionError("RFP not found", missing_key="rfp")
        # Just verify it doesn't crash - UI testing requires Streamlit environment
        result = handle_error(error, show_ui_error=False)
        assert result is None


class TestHandleErrorsDecorator:
    """Test @handle_errors decorator."""
    
    def test_decorator_success(self):
        """Test decorator with successful function."""
        @handle_errors(fallback_data=None)
        def success_func():
            return "success"
        
        result = success_func()
        assert result == "success"
    
    def test_decorator_with_error(self, caplog):
        """Test decorator catching error."""
        import logging
        caplog.set_level(logging.ERROR)
        
        @handle_errors(fallback_data="fallback", show_ui=False)
        def error_func():
            raise AppError("Test error")
        
        result = error_func()
        assert result == "fallback"
        assert "AppError" in caplog.text
    
    def test_decorator_with_args(self):
        """Test decorator with function arguments."""
        @handle_errors(fallback_data=0, show_ui=False)
        def add_numbers(a, b):
            if a < 0:
                raise ValidationError("Negative number")
            return a + b
        
        # Success case
        result = add_numbers(5, 3)
        assert result == 8
        
        # Error case
        result = add_numbers(-1, 3)
        assert result == 0
    
    def test_decorator_with_kwargs(self):
        """Test decorator with keyword arguments."""
        @handle_errors(fallback_data={}, show_ui=False)
        def create_dict(key, value=None):
            if value is None:
                raise ValidationError("Value required")
            return {key: value}
        
        # Success case
        result = create_dict("name", value="John")
        assert result == {"name": "John"}
        
        # Error case
        result = create_dict("name")
        assert result == {}
    
    def test_decorator_custom_context(self, caplog):
        """Test decorator with custom context."""
        import logging
        caplog.set_level(logging.ERROR)
        
        @handle_errors(
            fallback_data=None,
            show_ui=False,
            context={"component": "test"}
        )
        def error_func():
            raise AppError("Test error")
        
        error_func()
        assert "Test error" in caplog.text
    
    def test_decorator_preserves_function_name(self):
        """Test that decorator preserves function name."""
        @handle_errors(fallback_data=None)
        def my_function():
            """My docstring."""
            pass
        
        assert my_function.__name__ == "my_function"
        assert my_function.__doc__ == "My docstring."


class TestGetErrorSummary:
    """Test get_error_summary utility function."""
    
    def test_summary_basic_exception(self):
        """Test summary for basic Exception."""
        error = Exception("Basic error")
        summary = get_error_summary(error)
        
        assert summary["type"] == "Exception"
        assert summary["message"] == "Basic error"
        assert "user_message" not in summary
    
    def test_summary_app_error(self):
        """Test summary for AppError."""
        error = AppError(
            "Technical error",
            context={"file": "test.py"},
            user_message="User error"
        )
        summary = get_error_summary(error)
        
        assert summary["type"] == "AppError"
        assert summary["message"] == "Technical error (file=test.py)"
        assert summary["user_message"] == "User error"
        assert summary["context"] == {"file": "test.py"}
    
    def test_summary_llm_error(self):
        """Test summary for LLMError."""
        error = LLMError(
            "Rate limit",
            error_code="RATE_LIMIT",
            retry_after=60
        )
        summary = get_error_summary(error)
        
        assert summary["type"] == "LLMError"
        assert summary["error_code"] == "RATE_LIMIT"
        assert summary["retry_after"] == 60
    
    def test_summary_validation_error(self):
        """Test summary for ValidationError."""
        error = ValidationError(
            "Invalid format",
            field="email",
            expected="user@example.com"
        )
        summary = get_error_summary(error)
        
        assert summary["type"] == "ValidationError"
        assert summary["field"] == "email"
        assert summary["expected"] == "user@example.com"
    
    def test_summary_pdf_error(self):
        """Test summary for PDFError."""
        error = PDFError("Empty file", pdf_path="/path/to/file.pdf")
        summary = get_error_summary(error)
        
        assert summary["type"] == "PDFError"
        assert summary["pdf_path"] == "/path/to/file.pdf"
    
    def test_summary_session_error(self):
        """Test summary for SessionError."""
        error = SessionError("Missing data", missing_key="rfp")
        summary = get_error_summary(error)
        
        assert summary["type"] == "SessionError"
        assert summary["missing_key"] == "rfp"


class TestUIFeedback:
    """Test UI feedback functions."""
    
    def test_llm_error_rate_limit_ui(self):
        """Test UI for rate limit error."""
        from src.utils.error_handler import _handle_llm_error_ui
        
        error = LLMError(
            "Rate limit",
            error_code="RATE_LIMIT",
            retry_after=60
        )
        assert error.error_code == "RATE_LIMIT"
        assert error.retry_after == 60
        
        # Test that the function can be called (UI rendering requires Streamlit)
        # We just verify it doesn't crash
        try:
            _handle_llm_error_ui(error, allow_retry=False)
        except ImportError:
            # Expected if Streamlit is not available
            pass
    
    def test_llm_error_invalid_key_ui(self):
        """Test UI for invalid key error."""
        from src.utils.error_handler import _handle_llm_error_ui
        
        error = LLMError("Invalid key", error_code="INVALID_KEY")
        assert error.error_code == "INVALID_KEY"
        
        try:
            _handle_llm_error_ui(error, allow_retry=False)
        except ImportError:
            pass
    
    def test_llm_error_empty_response_ui(self):
        """Test UI for empty response error."""
        from src.utils.error_handler import _handle_llm_error_ui
        
        error = LLMError("Empty", error_code="EMPTY_RESPONSE")
        assert error.error_code == "EMPTY_RESPONSE"
        
        try:
            _handle_llm_error_ui(error, allow_retry=False)
        except ImportError:
            pass
    
    def test_llm_error_generic_ui(self):
        """Test UI for generic LLM error."""
        from src.utils.error_handler import _handle_llm_error_ui
        
        error = LLMError("Generic error", error_code="OTHER")
        
        try:
            _handle_llm_error_ui(error, allow_retry=False)
        except ImportError:
            pass
    
    def test_llm_error_with_retry_ui(self):
        """Test UI for LLM error with retry button."""
        from src.utils.error_handler import _handle_llm_error_ui
        
        error = LLMError("Timeout", error_code="TIMEOUT")
        
        try:
            _handle_llm_error_ui(error, allow_retry=True)
        except ImportError:
            pass
    
    def test_validation_error_ui(self):
        """Test UI for validation error."""
        from src.utils.error_handler import _handle_validation_error_ui
        
        error = ValidationError(
            "Invalid email",
            field="email",
            expected="user@example.com"
        )
        
        try:
            _handle_validation_error_ui(error)
        except ImportError:
            pass
    
    def test_pdf_error_ui(self):
        """Test UI for PDF error."""
        from src.utils.error_handler import _handle_pdf_error_ui
        
        error = PDFError("Empty PDF", pdf_path="test.pdf")
        
        try:
            _handle_pdf_error_ui(error)
        except ImportError:
            pass
    
    def test_session_error_rfp_missing_ui(self):
        """Test UI for missing RFP session error."""
        from src.utils.error_handler import _handle_session_error_ui
        
        error = SessionError("No RFP", missing_key="rfp")
        assert error.missing_key == "rfp"
        
        try:
            _handle_session_error_ui(error)
        except ImportError:
            pass
    
    def test_session_error_other_key_ui(self):
        """Test UI for session error with non-RFP key."""
        from src.utils.error_handler import _handle_session_error_ui
        
        error = SessionError("Missing data", missing_key="other_key")
        
        try:
            _handle_session_error_ui(error)
        except ImportError:
            pass

