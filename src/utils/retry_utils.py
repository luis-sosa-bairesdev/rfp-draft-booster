"""
Retry logic with exponential backoff using tenacity.

This module provides:
- Retry decorators for LLM calls
- Exponential backoff configuration
- Logging before retry attempts
"""

import logging
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

# Import error classes
from src.utils.error_handler import LLMError

logger = logging.getLogger(__name__)


# ============================================================================
# Retry Decorators
# ============================================================================

# Retry decorator for LLM calls
# - Retry up to 3 times
# - Exponential backoff: 2s, 4s, 8s (up to 10s max)
# - Only retry on LLM errors, connection errors, or timeouts
# - Log warning before each retry
retry_llm_call = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((LLMError, ConnectionError, TimeoutError)),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True
)


# ============================================================================
# Usage Examples (for documentation)
# ============================================================================

# Example 1: Using as decorator
# @retry_llm_call
# def extract_requirements(text: str) -> List[Requirement]:
#     # LLM call that might fail
#     response = llm_client.generate(prompt, timeout=120)
#     return parse_response(response)

# Example 2: Combining with error handler
# @retry_llm_call
# @handle_errors(fallback_data=[], show_ui=True)
# def extract_requirements(text: str) -> List[Requirement]:
#     # LLM call with automatic retry and error handling
#     response = llm_client.generate(prompt, timeout=120)
#     if not response:
#         raise LLMError("Empty response", error_code="EMPTY_RESPONSE")
#     return parse_response(response)

