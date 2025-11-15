"""
Unit tests for prompt templates.

Tests cover:
- Prompt template generation functions
"""

from utils.prompt_templates import (
    get_extraction_prompt,
    get_risk_detection_prompt,
    get_draft_generation_prompt,
    get_ai_assistant_prompt
)


class TestPromptTemplates:
    """Test prompt template functions."""
    
    def test_extraction_prompt(self):
        """Test requirement extraction prompt generation."""
        prompt = get_extraction_prompt(
            rfp_text="Sample RFP text",
            page_number=1
        )
        
        assert prompt is not None
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "Sample RFP text" in prompt
    
    def test_risk_detection_prompt(self):
        """Test risk detection prompt generation."""
        prompt = get_risk_detection_prompt(
            rfp_text="Sample clause text",
            page_number=1
        )
        
        assert prompt is not None
        assert isinstance(prompt, str)
        assert len(prompt) > 0
    
    def test_draft_generation_prompt(self):
        """Test draft generation prompt."""
        prompt = get_draft_generation_prompt(
            rfp_info="Test RFP Info",
            requirements_summary="Summary",
            service_matches="Service matches",
            risks_summary="Risks"
        )
        
        assert prompt is not None
        assert isinstance(prompt, str)
        assert len(prompt) > 0
    
    def test_ai_assistant_prompt(self):
        """Test AI assistant prompt."""
        prompt = get_ai_assistant_prompt(
            question="What is this?",
            context={}
        )
        
        assert prompt is not None
        assert isinstance(prompt, str)
        assert "What is this?" in prompt
