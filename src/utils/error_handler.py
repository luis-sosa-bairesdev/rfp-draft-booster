"""
Centralized error handling with custom exception classes and UI feedback.

This module provides:
- Custom exception classes for different error types
- Centralized error handling function
- Decorator for wrapping functions with error handling
- UI feedback functions for Streamlit
"""

import logging
from typing import Any, Optional, Callable, Dict
from functools import wraps

logger = logging.getLogger(__name__)


# ============================================================================
# Custom Exception Classes
# ============================================================================

class AppError(Exception):
    """Base exception for all application errors."""
    
    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None
    ):
        """
        Initialize application error.
        
        Args:
            message: Technical error message for logging
            context: Additional context for debugging
            user_message: User-friendly message for UI display
        """
        self.message = message
        self.context = context or {}
        self.user_message = user_message or message
        super().__init__(self.message)
    
    def __str__(self) -> str:
        """String representation with context."""
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{self.message} ({context_str})"
        return self.message


class LLMError(AppError):
    """LLM API errors (rate limit, timeout, invalid key, empty response)."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        retry_after: Optional[int] = None,
        **kwargs
    ):
        """
        Initialize LLM error.
        
        Args:
            message: Error message
            error_code: Error code (e.g., "RATE_LIMIT", "TIMEOUT", "INVALID_KEY")
            retry_after: Seconds to wait before retry
            **kwargs: Additional arguments for AppError
        """
        super().__init__(message, **kwargs)
        self.error_code = error_code
        self.retry_after = retry_after


class ValidationError(AppError):
    """Input validation errors."""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        expected: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize validation error.
        
        Args:
            message: Error message
            field: Field that failed validation
            expected: Expected value or format
            **kwargs: Additional arguments for AppError
        """
        super().__init__(message, **kwargs)
        self.field = field
        self.expected = expected


class PDFError(AppError):
    """PDF processing errors."""
    
    def __init__(
        self,
        message: str,
        pdf_path: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize PDF error.
        
        Args:
            message: Error message
            pdf_path: Path to the PDF file
            **kwargs: Additional arguments for AppError
        """
        super().__init__(message, **kwargs)
        self.pdf_path = pdf_path


class SessionError(AppError):
    """Session state errors (missing data, cleared state)."""
    
    def __init__(
        self,
        message: str,
        missing_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize session error.
        
        Args:
            message: Error message
            missing_key: Session state key that is missing
            **kwargs: Additional arguments for AppError
        """
        super().__init__(message, **kwargs)
        self.missing_key = missing_key


# ============================================================================
# Error Handler Functions
# ============================================================================

def handle_error(
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    fallback_data: Any = None,
    show_ui_error: bool = True,
    allow_retry: bool = True
) -> Any:
    """
    Centralized error handler with logging and UI feedback.
    
    Args:
        error: The exception to handle
        context: Additional context for logging
        fallback_data: Data to return if error occurs
        show_ui_error: Whether to show error in Streamlit UI
        allow_retry: Whether to show retry button
    
    Returns:
        fallback_data if provided, else None
    """
    context = context or {}
    
    # Log error with full context
    logger.error(
        f"{error.__class__.__name__}: {str(error)}",
        extra=context,
        exc_info=True
    )
    
    # Show UI feedback if requested
    if show_ui_error:
        try:
            import streamlit as st
            
            if isinstance(error, LLMError):
                _handle_llm_error_ui(error, allow_retry)
            elif isinstance(error, ValidationError):
                _handle_validation_error_ui(error)
            elif isinstance(error, PDFError):
                _handle_pdf_error_ui(error)
            elif isinstance(error, SessionError):
                _handle_session_error_ui(error)
            else:
                st.error(f"❌ {error.__class__.__name__}: {str(error)}")
                if allow_retry:
                    if st.button("🔄 Retry", key=f"retry_{id(error)}"):
                        st.rerun()
        except ImportError:
            # Streamlit not available (e.g., in tests)
            logger.warning("Streamlit not available for UI error display")
    
    return fallback_data


def _handle_llm_error_ui(error: LLMError, allow_retry: bool):
    """Handle LLM error UI feedback."""
    import streamlit as st
    
    if error.error_code == "RATE_LIMIT":
        retry_msg = f"Retry in {error.retry_after} seconds." if error.retry_after else "Please try again later."
        st.warning(
            f"⚠️ **API Rate Limit Reached**\n\n"
            f"The LLM service has hit its rate limit. {retry_msg}"
        )
    elif error.error_code == "TIMEOUT":
        st.error(
            "❌ **Request Timed Out**\n\n"
            "The LLM service took too long to respond. This can happen with large documents."
        )
    elif error.error_code == "INVALID_KEY":
        st.error(
            "❌ **Invalid API Key**\n\n"
            "Your LLM API key is invalid or expired. Please check your configuration.\n\n"
            "📚 [Get API Key from Google AI Studio](https://makersuite.google.com)"
        )
    elif error.error_code == "EMPTY_RESPONSE":
        st.warning(
            "⚠️ **Empty Response from LLM**\n\n"
            "The LLM returned an empty response. This can happen occasionally."
        )
    else:
        st.error(f"❌ **LLM Error:** {error.user_message}")
    
    # Offer retry and mock data fallback
    if allow_retry:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Retry", key=f"retry_llm_{id(error)}"):
                st.rerun()
        with col2:
            use_mock = st.radio(
                "Use mock data instead?",
                ["No", "Yes, use mock data"],
                key=f"mock_llm_{id(error)}",
                horizontal=True,
                label_visibility="collapsed"
            )
            if use_mock == "Yes, use mock data":
                st.session_state.use_mock_data = True
                st.rerun()


def _handle_validation_error_ui(error: ValidationError):
    """Handle validation error UI feedback."""
    import streamlit as st
    
    error_msg = f"❌ **Validation Error**\n\n"
    if error.field:
        error_msg += f"Field: `{error.field}`\n\n"
    error_msg += f"Issue: {error.user_message}"
    if error.expected:
        error_msg += f"\n\nExpected: {error.expected}"
    
    st.error(error_msg)


def _handle_pdf_error_ui(error: PDFError):
    """Handle PDF error UI feedback."""
    import streamlit as st
    
    error_msg = f"❌ **PDF Processing Error**\n\n{error.user_message}"
    if error.pdf_path:
        error_msg += f"\n\nFile: `{error.pdf_path}`"
    
    st.error(error_msg)


def _handle_session_error_ui(error: SessionError):
    """Handle session error UI feedback."""
    import streamlit as st
    
    st.warning(f"⚠️ **Session Error**\n\n{error.user_message}")
    
    if error.missing_key == "rfp":
        st.info("📤 Please upload an RFP to continue.")
        if st.button("Go to Upload Page", key="goto_upload"):
            st.switch_page("pages/1_📤_Upload_RFP.py")


# ============================================================================
# Decorator for Error Handling
# ============================================================================

def handle_errors(
    fallback_data: Any = None,
    show_ui: bool = True,
    allow_retry: bool = True,
    context: Optional[Dict[str, Any]] = None
):
    """
    Decorator to wrap functions with error handling.
    
    Usage:
        @handle_errors(fallback_data=[], show_ui=True)
        def extract_requirements(text: str) -> List[Requirement]:
            # ... LLM call that might fail
    
    Args:
        fallback_data: Data to return if error occurs
        show_ui: Whether to show error in Streamlit UI
        allow_retry: Whether to show retry button
        context: Additional context for logging
    
    Returns:
        Decorated function that handles errors
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as error:
                return handle_error(
                    error=error,
                    context=context or {"function": func.__name__},
                    fallback_data=fallback_data,
                    show_ui_error=show_ui,
                    allow_retry=allow_retry
                )
        return wrapper
    return decorator


# ============================================================================
# Utility Functions
# ============================================================================

def get_error_summary(error: Exception) -> Dict[str, Any]:
    """
    Get a summary of an error for logging or display.
    
    Args:
        error: The exception to summarize
    
    Returns:
        Dictionary with error details
    """
    summary = {
        "type": error.__class__.__name__,
        "message": str(error)
    }
    
    if isinstance(error, AppError):
        summary["user_message"] = error.user_message
        summary["context"] = error.context
        
        if isinstance(error, LLMError):
            summary["error_code"] = error.error_code
            summary["retry_after"] = error.retry_after
        elif isinstance(error, ValidationError):
            summary["field"] = error.field
            summary["expected"] = error.expected
        elif isinstance(error, PDFError):
            summary["pdf_path"] = error.pdf_path
        elif isinstance(error, SessionError):
            summary["missing_key"] = error.missing_key
    
    return summary

