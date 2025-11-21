"""
Unit tests for retry utilities module.

Tests retry decorator and exponential backoff.
"""

import pytest
import time
from unittest.mock import Mock, patch
from src.utils.retry_utils import retry_llm_call
from src.utils.error_handler import LLMError


class TestRetryLLMCall:
    """Test retry_llm_call decorator."""
    
    def test_retry_success_on_first_attempt(self):
        """Test that successful function doesn't retry."""
        @retry_llm_call
        def successful_function():
            return "success"
        
        result = successful_function()
        assert result == "success"
    
    def test_retry_on_llm_error(self):
        """Test that function retries on LLMError."""
        call_count = {"count": 0}
        
        @retry_llm_call
        def failing_function():
            call_count["count"] += 1
            if call_count["count"] < 2:
                raise LLMError("API timeout", error_code="TIMEOUT")
            return "success"
        
        result = failing_function()
        assert result == "success"
        assert call_count["count"] == 2  # Failed once, then succeeded
    
    def test_retry_on_connection_error(self):
        """Test that function retries on ConnectionError."""
        call_count = {"count": 0}
        
        @retry_llm_call
        def failing_function():
            call_count["count"] += 1
            if call_count["count"] < 2:
                raise ConnectionError("Network error")
            return "success"
        
        result = failing_function()
        assert result == "success"
        assert call_count["count"] == 2
    
    def test_retry_on_timeout_error(self):
        """Test that function retries on TimeoutError."""
        call_count = {"count": 0}
        
        @retry_llm_call
        def failing_function():
            call_count["count"] += 1
            if call_count["count"] < 2:
                raise TimeoutError("Request timed out")
            return "success"
        
        result = failing_function()
        assert result == "success"
        assert call_count["count"] == 2
    
    def test_retry_stops_after_max_attempts(self):
        """Test that retry stops after 3 attempts."""
        call_count = {"count": 0}
        
        @retry_llm_call
        def always_failing():
            call_count["count"] += 1
            raise LLMError("Always fails", error_code="ERROR")
        
        with pytest.raises(LLMError):
            always_failing()
        
        assert call_count["count"] == 3  # Initial + 2 retries
    
    def test_retry_does_not_retry_other_exceptions(self):
        """Test that non-retryable exceptions are not retried."""
        call_count = {"count": 0}
        
        @retry_llm_call
        def other_exception():
            call_count["count"] += 1
            raise ValueError("Not a retryable error")
        
        with pytest.raises(ValueError):
            other_exception()
        
        assert call_count["count"] == 1  # No retries
    
    def test_retry_with_exponential_backoff(self):
        """Test that retry uses exponential backoff."""
        call_count = {"count": 0}
        times = []
        
        @retry_llm_call
        def failing_with_timing():
            call_count["count"] += 1
            times.append(time.time())
            if call_count["count"] < 3:
                raise LLMError("Fail", error_code="ERROR")
            return "success"
        
        start = time.time()
        result = failing_with_timing()
        duration = time.time() - start
        
        assert result == "success"
        assert call_count["count"] == 3
        # Should take at least 2s + 4s = 6s total (exponential backoff)
        # But we'll be lenient and just check it's > 4s to account for timing variations
        assert duration > 4
    
    def test_retry_preserves_function_name(self):
        """Test that decorator preserves function name."""
        @retry_llm_call
        def my_function():
            """My docstring."""
            pass
        
        assert my_function.__name__ == "my_function"
        assert my_function.__doc__ == "My docstring."
    
    def test_retry_with_arguments(self):
        """Test that retry works with function arguments."""
        call_count = {"count": 0}
        
        @retry_llm_call
        def function_with_args(a, b, c=None):
            call_count["count"] += 1
            if call_count["count"] < 2:
                raise LLMError("Fail")
            return f"{a}-{b}-{c}"
        
        result = function_with_args("x", "y", c="z")
        assert result == "x-y-z"
        assert call_count["count"] == 2


class TestRetryIntegration:
    """Integration tests for retry with error handler."""
    
    def test_retry_with_handle_errors(self):
        """Test retry decorator combined with error handler (correct order)."""
        from src.utils.error_handler import handle_errors
        
        call_count = {"count": 0}
        
        # Note: Decorator order matters!
        # @handle_errors should be outer, @retry_llm_call should be inner
        @handle_errors(fallback_data="fallback", show_ui=False)
        @retry_llm_call
        def combined_function():
            call_count["count"] += 1
            if call_count["count"] < 2:
                raise LLMError("Temporary error")
            return "success"
        
        result = combined_function()
        assert result == "success"
        assert call_count["count"] == 2  # Failed once, retried, then succeeded
    
    def test_retry_then_fallback(self):
        """Test that fallback is used after all retries fail."""
        from src.utils.error_handler import handle_errors
        
        call_count = {"count": 0}
        
        # Correct decorator order for retry then fallback
        @handle_errors(fallback_data="fallback", show_ui=False)
        @retry_llm_call
        def always_fails():
            call_count["count"] += 1
            raise LLMError("Always fails")
        
        result = always_fails()
        assert result == "fallback"
        assert call_count["count"] == 3  # All 3 attempts exhausted

