"""
Unit tests for Draft model.

Tests cover:
- Draft creation and validation
- DraftStatus and GenerationMethod enums
- DraftSection model
- Draft JSON serialization/deserialization
- Helper methods and calculations
"""

import pytest
from datetime import datetime
from models.draft import (
    Draft, 
    DraftStatus, 
    DraftSection, 
    GenerationMethod
)


class TestDraftSection:
    """Test DraftSection model."""
    
    def test_create_draft_section(self):
        """Test creating a draft section."""
        section = DraftSection(
            title="Executive Summary",
            content="This is the executive summary content.",
            section_type="executive_summary",
            word_count=100,
            order=1
        )
        
        assert section.title == "Executive Summary"
        assert section.content == "This is the executive summary content."
        assert section.section_type == "executive_summary"
        assert section.word_count == 100
        assert section.order == 1


class TestDraftModel:
    """Test Draft model creation and validation."""
    
    def test_create_draft_with_defaults(self):
        """Test creating a draft with default values."""
        draft = Draft(
            rfp_id="rfp-001",
            title="Test RFP Draft"
        )
        
        assert draft.rfp_id == "rfp-001"
        assert draft.title == "Test RFP Draft"
        assert draft.status == DraftStatus.GENERATED
        assert draft.generated_by == GenerationMethod.AI
        assert draft.sections == []
        assert draft.word_count == 0
    
    def test_create_draft_with_sections(self):
        """Test creating a draft with sections."""
        sections = [
            DraftSection(
                section_type="introduction",
                title="Introduction",
                content="Intro content",
                word_count=50,
                order=1
            )
        ]
        
        draft = Draft(
            rfp_id="rfp-002",
            title="Test Draft",
            sections=sections,
            word_count=50
        )
        
        assert len(draft.sections) == 1
        assert draft.word_count == 50
        assert draft.sections[0].title == "Introduction"
    
    def test_draft_to_dict(self):
        """Test converting draft to dictionary."""
        draft = Draft(
            rfp_id="rfp-003",
            title="Export Test",
            content="Full content here",
            word_count=100
        )
        
        draft_dict = draft.to_dict()
        
        assert draft_dict["rfp_id"] == "rfp-003"
        assert draft_dict["title"] == "Export Test"
        assert draft_dict["status"] == "generated"
        assert draft_dict["generated_by"] == "ai"
        assert draft_dict["word_count"] == 100
    
    def test_draft_from_dict(self):
        """Test creating draft from dictionary."""
        data = {
            "id": "draft-001",
            "rfp_id": "rfp-004",
            "title": "Import Test",
            "status": "generated",
            "generated_by": "manual",
            "content": "Content",
            "sections": [],
            "word_count": 75
        }
        
        draft = Draft.from_dict(data)
        
        assert draft.rfp_id == "rfp-004"
        assert draft.title == "Import Test"
        assert draft.status == DraftStatus.GENERATED
        assert draft.generated_by == GenerationMethod.MANUAL


class TestDraftStatus:
    """Test DraftStatus enum."""
    
    def test_draft_status_values(self):
        """Test all draft status values."""
        assert DraftStatus.GENERATED.value == "generated"
        assert DraftStatus.EDITING.value == "editing"
        assert DraftStatus.REVIEWED.value == "reviewed"
        assert DraftStatus.APPROVED.value == "approved"
        assert DraftStatus.EXPORTED.value == "exported"


class TestGenerationMethod:
    """Test GenerationMethod enum."""
    
    def test_generation_method_values(self):
        """Test all generation method values."""
        assert GenerationMethod.AI.value == "ai"
        assert GenerationMethod.MANUAL.value == "manual"
        assert GenerationMethod.HYBRID.value == "hybrid"


class TestDraftCalculations:
    """Test draft calculations and helper methods."""
    
    def test_word_count_tracking(self):
        """Test word count tracking."""
        sections = [
            DraftSection(
                section_type="introduction",
                title="Section 1",
                content="Content 1",
                word_count=100,
                order=1
            ),
            DraftSection(
                section_type="approach",
                title="Section 2",
                content="Content 2",
                word_count=200,
                order=2
            )
        ]
        
        draft = Draft(
            rfp_id="rfp-006",
            title="Word Count Test",
            sections=sections,
            word_count=300
        )
        
        assert draft.word_count == 300
        assert len(draft.sections) == 2

