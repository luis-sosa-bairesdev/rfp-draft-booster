"""
Unit tests for Requirement Extractor.

Tests cover:
- Requirement extraction from RFP text
- Page-by-page extraction
- Text chunking for large documents
- Deduplication logic
- Confidence filtering
- Error handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from models import RFP, RFPStatus, Requirement, RequirementCategory, RequirementPriority
from services.requirement_extractor import RequirementExtractor, extract_requirements_from_rfp


class TestRequirementExtractor:
    """Test RequirementExtractor service."""
    
    def test_initialization(self):
        """Test extractor initialization."""
        mock_client = Mock()
        extractor = RequirementExtractor(llm_client=mock_client, min_confidence=0.5)
        
        assert extractor.llm_client == mock_client
        assert extractor.min_confidence == 0.5
    
    def test_initialization_with_defaults(self):
        """Test extractor uses default client if not provided."""
        with patch('services.requirement_extractor.create_llm_client') as mock_create:
            mock_client = Mock()
            mock_create.return_value = mock_client
            
            extractor = RequirementExtractor()
            
            assert extractor.llm_client == mock_client
            assert extractor.min_confidence == 0.3
            mock_create.assert_called_once_with(fallback=True)
    
    def test_extract_from_rfp_no_text_raises_error(self):
        """Test error when RFP has no extracted text."""
        mock_client = Mock()
        extractor = RequirementExtractor(llm_client=mock_client)
        
        rfp = RFP(id="test", filename="test.pdf")
        rfp.extracted_text = None
        
        with pytest.raises(ValueError, match="RFP must have extracted_text"):
            extractor.extract_from_rfp(rfp)
    
    def test_extract_from_simple_text(self):
        """Test extraction from simple RFP text."""
        # Mock LLM client responses
        mock_client = Mock()
        mock_client.generate.return_value = "LLM response"
        mock_client.extract_json.return_value = [
            {
                "description": "System must support 99.9% uptime",
                "category": "technical",
                "priority": "critical",
                "confidence": 0.95,
                "page_number": 1
            },
            {
                "description": "Project completion within 60 days",
                "category": "timeline",
                "priority": "high",
                "confidence": 0.90,
                "page_number": 1
            }
        ]
        
        extractor = RequirementExtractor(llm_client=mock_client, min_confidence=0.5)
        
        rfp = RFP(id="test-rfp", filename="test.pdf")
        rfp.extracted_text = "System requirements: 99.9% uptime. Timeline: 60 days."
        
        requirements = extractor.extract_from_rfp(rfp)
        
        assert len(requirements) == 2
        assert requirements[0].description == "System must support 99.9% uptime"
        assert requirements[0].category == RequirementCategory.TECHNICAL
        assert requirements[0].priority == RequirementPriority.CRITICAL
        assert requirements[0].confidence == 0.95
        assert requirements[1].description == "Project completion within 60 days"
    
    def test_extract_with_confidence_filtering(self):
        """Test requirements below min_confidence are filtered out."""
        mock_client = Mock()
        mock_client.generate.return_value = "LLM response"
        mock_client.extract_json.return_value = [
            {"description": "High confidence req", "category": "technical", 
             "priority": "high", "confidence": 0.90},
            {"description": "Low confidence req", "category": "functional", 
             "priority": "medium", "confidence": 0.20},
            {"description": "Medium confidence req", "category": "budget", 
             "priority": "high", "confidence": 0.60},
        ]
        
        extractor = RequirementExtractor(llm_client=mock_client, min_confidence=0.5)
        
        rfp = RFP(id="test", filename="test.pdf")
        rfp.extracted_text = "Test requirements"
        
        requirements = extractor.extract_from_rfp(rfp)
        
        # Only 2 requirements should pass (confidence >= 0.5)
        assert len(requirements) == 2
        assert all(req.confidence >= 0.5 for req in requirements)
    
    def test_extract_by_page(self):
        """Test extraction page by page."""
        mock_client = Mock()
        mock_client.generate.return_value = "LLM response"
        mock_client.extract_json.side_effect = [
            [{"description": "Req from page 1", "category": "technical", 
              "priority": "high", "confidence": 0.85}],
            [{"description": "Req from page 2", "category": "functional", 
              "priority": "medium", "confidence": 0.75}],
        ]
        
        extractor = RequirementExtractor(llm_client=mock_client)
        
        rfp = RFP(id="test", filename="test.pdf")
        rfp.extracted_text_by_page = {
            1: "Page 1 content with requirements",
            2: "Page 2 content with different requirements"
        }
        
        requirements = extractor.extract_from_rfp(rfp)
        
        assert len(requirements) == 2
        # Verify both pages were processed
        assert mock_client.generate.call_count == 2
    
    def test_deduplication(self):
        """Test duplicate requirements are removed."""
        mock_client = Mock()
        mock_client.generate.return_value = "LLM response"
        mock_client.extract_json.side_effect = [
            [{"description": "Must support 99.9% uptime", "category": "technical", 
              "priority": "critical", "confidence": 0.95}],
            [{"description": "Must support 99.9% uptime", "category": "technical", 
              "priority": "critical", "confidence": 0.95}],  # Duplicate
        ]
        
        extractor = RequirementExtractor(llm_client=mock_client)
        
        rfp = RFP(id="test", filename="test.pdf")
        rfp.extracted_text_by_page = {
            1: "Page 1 content",
            2: "Page 2 content"
        }
        
        requirements = extractor.extract_from_rfp(rfp)
        
        # Only 1 unique requirement
        assert len(requirements) == 1
    
    def test_text_chunking(self):
        """Test large text is chunked properly."""
        mock_client = Mock()
        extractor = RequirementExtractor(llm_client=mock_client)
        
        # Create text larger than MAX_CHUNK_SIZE
        large_text = "A" * 5000  # 5000 characters
        chunks = extractor._chunk_text(large_text)
        
        assert len(chunks) > 1
        # Check chunks overlap
        assert len(chunks[0]) <= 4000  # MAX_CHUNK_SIZE from prompt_templates
    
    def test_create_requirement_from_data(self):
        """Test creating Requirement from LLM response data."""
        mock_client = Mock()
        extractor = RequirementExtractor(llm_client=mock_client)
        
        data = {
            "description": "Must be HIPAA compliant",
            "category": "compliance",
            "priority": "critical",
            "confidence": 0.98,
            "page_number": 5
        }
        
        req = extractor._create_requirement(data, "test-rfp-1", None)
        
        assert req.rfp_id == "test-rfp-1"
        assert req.description == "Must be HIPAA compliant"
        assert req.category == RequirementCategory.COMPLIANCE
        assert req.priority == RequirementPriority.CRITICAL
        assert req.confidence == 0.98
        assert req.page_number == 5
    
    def test_create_requirement_with_invalid_category(self):
        """Test invalid category defaults to functional."""
        mock_client = Mock()
        extractor = RequirementExtractor(llm_client=mock_client)
        
        data = {
            "description": "Test",
            "category": "invalid_category",
            "priority": "high",
            "confidence": 0.8
        }
        
        req = extractor._create_requirement(data, "test-rfp", None)
        
        assert req.category == RequirementCategory.FUNCTIONAL
    
    def test_create_requirement_with_invalid_priority(self):
        """Test invalid priority defaults to medium."""
        mock_client = Mock()
        extractor = RequirementExtractor(llm_client=mock_client)
        
        data = {
            "description": "Test",
            "category": "technical",
            "priority": "invalid_priority",
            "confidence": 0.8
        }
        
        req = extractor._create_requirement(data, "test-rfp", None)
        
        assert req.priority == RequirementPriority.MEDIUM
    
    def test_create_requirement_clamps_confidence(self):
        """Test confidence is clamped to valid range."""
        mock_client = Mock()
        extractor = RequirementExtractor(llm_client=mock_client)
        
        # Test confidence > 1.0
        data = {
            "description": "Test",
            "category": "technical",
            "priority": "high",
            "confidence": 1.5
        }
        
        req = extractor._create_requirement(data, "test-rfp", None)
        assert req.confidence == 1.0
        
        # Test confidence < 0.0
        data["confidence"] = -0.5
        req = extractor._create_requirement(data, "test-rfp", None)
        assert req.confidence == 0.0
    
    def test_refine_requirement(self):
        """Test requirement refinement using LLM."""
        mock_client = Mock()
        mock_client.generate.return_value = "Refined: System must maintain 99.9% uptime"
        
        extractor = RequirementExtractor(llm_client=mock_client)
        
        req = Requirement(
            rfp_id="test",
            description="System uptime should be good",
            category=RequirementCategory.TECHNICAL,
            priority=RequirementPriority.HIGH
        )
        
        original_updated_at = req.updated_at
        refined = extractor.refine_requirement(req)
        
        assert "Refined" in refined.description
        assert refined.updated_at > original_updated_at
    
    def test_empty_page_text_skipped(self):
        """Test empty pages are skipped during extraction."""
        mock_client = Mock()
        mock_client.generate.return_value = "LLM response"
        mock_client.extract_json.return_value = [
            {"description": "Requirement", "category": "technical", 
             "priority": "high", "confidence": 0.85}
        ]
        
        extractor = RequirementExtractor(llm_client=mock_client)
        
        rfp = RFP(id="test", filename="test.pdf")
        rfp.extracted_text_by_page = {
            1: "Page 1 with content",
            2: "   ",  # Empty page (only whitespace)
            3: "",    # Empty page
        }
        
        requirements = extractor.extract_from_rfp(rfp)
        
        # Only page 1 should be processed
        assert mock_client.generate.call_count == 1


class TestConvenienceFunction:
    """Test convenience function for extraction."""
    
    def test_extract_requirements_from_rfp(self):
        """Test convenience function works correctly."""
        with patch('services.requirement_extractor.RequirementExtractor') as mock_extractor_class:
            mock_extractor = Mock()
            mock_requirements = [Mock(), Mock()]
            mock_extractor.extract_from_rfp.return_value = mock_requirements
            mock_extractor_class.return_value = mock_extractor
            
            rfp = RFP(id="test", filename="test.pdf")
            rfp.extracted_text = "Test content"
            
            result = extract_requirements_from_rfp(rfp, min_confidence=0.7)
            
            mock_extractor_class.assert_called_once()
            assert result == mock_requirements

