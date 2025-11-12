"""
Tests for prompt templates.
"""

import pytest
from utils.prompt_templates import (
    get_extraction_prompt,
    get_refinement_prompt,
    get_categorization_prompt,
    get_prioritization_prompt,
    MAX_CHUNK_SIZE,
    CHUNK_OVERLAP,
)


class TestPromptTemplates:
    """Test prompt template functions."""
    
    def test_get_extraction_prompt_with_page(self):
        """Test extraction prompt generation with page number."""
        prompt = get_extraction_prompt("Test RFP text", page_number=5)
        
        assert "Test RFP text" in prompt
        assert "page 5" in prompt
        assert "category" in prompt.lower()
        assert "priority" in prompt.lower()
        assert "confidence" in prompt.lower()
    
    def test_get_extraction_prompt_without_page(self):
        """Test extraction prompt generation without page number."""
        prompt = get_extraction_prompt("Test RFP text")
        
        assert "Test RFP text" in prompt
        assert "unknown" in prompt or "page" in prompt.lower()
    
    def test_get_refinement_prompt(self):
        """Test refinement prompt generation."""
        requirement = {
            "description": "System must be fast",
            "category": "technical",
            "priority": "high"
        }
        
        prompt = get_refinement_prompt(requirement)
        
        assert "System must be fast" in prompt
        assert "technical" in prompt
        assert "high" in prompt
    
    def test_get_categorization_prompt(self):
        """Test categorization prompt generation."""
        prompt = get_categorization_prompt("System must support 99.9% uptime")
        
        assert "System must support 99.9% uptime" in prompt
        assert "category" in prompt.lower()
    
    def test_get_prioritization_prompt(self):
        """Test prioritization prompt generation."""
        prompt = get_prioritization_prompt("Must be HIPAA compliant")
        
        assert "Must be HIPAA compliant" in prompt
        assert "priority" in prompt.lower()
    
    def test_chunk_size_constants(self):
        """Test chunk size constants are defined."""
        assert MAX_CHUNK_SIZE > 0
        assert CHUNK_OVERLAP > 0
        assert CHUNK_OVERLAP < MAX_CHUNK_SIZE

