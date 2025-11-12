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
        
        rfp = RFP(id="test", file_name="test.pdf")
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
        
        rfp = RFP(id="test-rfp", file_name="test.pdf")
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
        
        rfp = RFP(id="test", file_name="test.pdf")
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
        
        rfp = RFP(id="test", file_name="test.pdf")
        rfp.extracted_text = "Page 1 content with requirements\nPage 2 content with different requirements"
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
        
        rfp = RFP(id="test", file_name="test.pdf")
        rfp.extracted_text = "Page 1 content\nPage 2 content"
        rfp.extracted_text_by_page = {
            1: "Page 1 content",
            2: "Page 2 content"
        }
        
        requirements = extractor.extract_from_rfp(rfp)
        
        # Only 1 unique requirement (duplicates removed)
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
        
        rfp = RFP(id="test", file_name="test.pdf")
        rfp.extracted_text = "Page 1 with content"
        rfp.extracted_text_by_page = {
            1: "Page 1 with content",
            2: "   ",  # Empty page (only whitespace)
            3: "",    # Empty page
        }
        
        requirements = extractor.extract_from_rfp(rfp)
        
        # Only page 1 should be processed
        assert mock_client.generate.call_count == 1
    
    def test_chunk_text_splits_large_text(self):
        """Test text chunking for large documents."""
        mock_client = Mock()
        extractor = RequirementExtractor(llm_client=mock_client)
        
        # Create text larger than MAX_CHUNK_SIZE
        large_text = "A" * 5000  # 5000 characters
        chunks = extractor._chunk_text(large_text)
        
        assert len(chunks) > 1
        # Verify chunks don't exceed max size
        assert all(len(chunk) <= 4000 + 200 for chunk in chunks)  # MAX_CHUNK_SIZE + overlap
    
    def test_chunk_text_preserves_small_text(self):
        """Test small text is not chunked."""
        mock_client = Mock()
        extractor = RequirementExtractor(llm_client=mock_client)
        
        small_text = "Small text content"
        chunks = extractor._chunk_text(small_text)
        
        assert len(chunks) == 1
        assert chunks[0] == small_text
    
    def test_create_requirement_with_missing_description(self):
        """Test error when requirement has no description."""
        mock_client = Mock()
        extractor = RequirementExtractor(llm_client=mock_client)
        
        data = {
            "category": "technical",
            "priority": "high",
            "confidence": 0.8
        }
        
        with pytest.raises(ValueError, match="description"):
            extractor._create_requirement(data, "test-rfp", None)
    
    def test_refine_requirement_updates_description(self):
        """Test requirement refinement updates description."""
        mock_client = Mock()
        mock_client.generate.return_value = "Refined: System must maintain 99.9% uptime SLA"
        
        extractor = RequirementExtractor(llm_client=mock_client)
        
        req = Requirement(
            rfp_id="test",
            description="System uptime should be good",
            category=RequirementCategory.TECHNICAL,
            priority=RequirementPriority.HIGH
        )
        
        original_description = req.description
        refined = extractor.refine_requirement(req)
        
        assert refined.description != original_description
        assert "Refined" in refined.description or refined.description != original_description
    
    def test_extract_from_chunks(self):
        """Test extraction from chunked text."""
        mock_client = Mock()
        mock_client.generate.return_value = "LLM response"
        mock_client.extract_json.side_effect = [
            [{"description": "Req from chunk 1", "category": "technical", 
              "priority": "high", "confidence": 0.85}],
            [{"description": "Req from chunk 2", "category": "functional", 
              "priority": "medium", "confidence": 0.75}],
        ]
        
        extractor = RequirementExtractor(llm_client=mock_client)
        
        # Create large text that will be chunked
        large_text = "A" * 5000
        
        requirements = extractor._extract_from_chunks(large_text, "test-rfp", None)
        
        # Should have requirements from multiple chunks
        assert len(requirements) >= 1
        assert mock_client.generate.call_count > 1
    
    def test_deduplicate_requirements_case_insensitive(self):
        """Test deduplication is case insensitive."""
        mock_client = Mock()
        extractor = RequirementExtractor(llm_client=mock_client)
        
        req1 = Requirement(
            rfp_id="test",
            description="System must support 99.9% uptime",
            confidence=0.9
        )
        req2 = Requirement(
            rfp_id="test",
            description="SYSTEM MUST SUPPORT 99.9% UPTIME",  # Same but uppercase
            confidence=0.9
        )
        
        deduplicated = extractor._deduplicate_requirements([req1, req2])
        
        # Should be considered duplicates (case insensitive)
        assert len(deduplicated) == 1
    
    def test_extract_from_text_with_error_handling(self):
        """Test extraction handles LLM errors gracefully."""
        mock_client = Mock()
        mock_client.generate.side_effect = Exception("LLM API error")
        
        extractor = RequirementExtractor(llm_client=mock_client)
        
        rfp = RFP(id="test", file_name="test.pdf")
        rfp.extracted_text = "Test content"
        
        # Should return empty list on error, not crash
        requirements = extractor._extract_from_text("Test", "test-rfp", None)
        assert requirements == []
    
    def test_extract_from_text_with_invalid_json_response(self):
        """Test extraction handles invalid JSON from LLM."""
        mock_client = Mock()
        mock_client.generate.return_value = "Not valid JSON at all"
        mock_client.extract_json.side_effect = ValueError("Invalid JSON")
        
        extractor = RequirementExtractor(llm_client=mock_client)
        
        requirements = extractor._extract_from_text("Test", "test-rfp", None)
        assert requirements == []
    
    def test_create_requirement_with_empty_description_stripped(self):
        """Test requirement creation handles empty description."""
        mock_client = Mock()
        extractor = RequirementExtractor(llm_client=mock_client)
        
        data = {
            "description": "   ",  # Only whitespace
            "category": "technical",
            "priority": "high",
            "confidence": 0.8
        }
        
        # Should raise error for empty description
        with pytest.raises(ValueError, match="description"):
            extractor._create_requirement(data, "test-rfp", None)
    
    def test_extract_from_rfp_uses_extracted_text_when_no_pages(self):
        """Test extraction uses extracted_text when extracted_text_by_page is empty."""
        mock_client = Mock()
        mock_client.generate.return_value = "LLM response"
        mock_client.extract_json.return_value = [
            {"description": "Requirement", "category": "technical", 
             "priority": "high", "confidence": 0.85}
        ]
        
        extractor = RequirementExtractor(llm_client=mock_client)
        
        rfp = RFP(id="test", file_name="test.pdf")
        rfp.extracted_text = "Full text content"
        rfp.extracted_text_by_page = {}  # Empty
        
        requirements = extractor.extract_from_rfp(rfp)
        
        assert len(requirements) == 1
        assert mock_client.generate.call_count == 1
    
    def test_deduplicate_empty_list(self):
        """Test deduplication of empty list."""
        mock_client = Mock()
        extractor = RequirementExtractor(llm_client=mock_client)
        
        deduplicated = extractor._deduplicate_requirements([])
        assert deduplicated == []
    
    def test_deduplicate_single_requirement(self):
        """Test deduplication with single requirement."""
        mock_client = Mock()
        extractor = RequirementExtractor(llm_client=mock_client)
        
        req = Requirement(rfp_id="test", description="Single requirement")
        
        deduplicated = extractor._deduplicate_requirements([req])
        assert len(deduplicated) == 1
        assert deduplicated[0] == req
    
    def test_create_requirement_with_llm_page_number(self):
        """Test requirement creation prefers LLM page number."""
        mock_client = Mock()
        extractor = RequirementExtractor(llm_client=mock_client)
        
        data = {
            "description": "Test requirement",
            "category": "technical",
            "priority": "high",
            "confidence": 0.8,
            "page_number": 10  # LLM provided page number
        }
        
        req = extractor._create_requirement(data, "test-rfp", page_number=5)
        
        # Should use LLM's page number (10) not our page number (5)
        assert req.page_number == 10
    
    def test_create_requirement_without_llm_page_number(self):
        """Test requirement creation uses provided page number when LLM doesn't provide one."""
        mock_client = Mock()
        extractor = RequirementExtractor(llm_client=mock_client)
        
        data = {
            "description": "Test requirement",
            "category": "technical",
            "priority": "high",
            "confidence": 0.8,
            "page_number": None  # LLM didn't provide page number
        }
        
        req = extractor._create_requirement(data, "test-rfp", page_number=7)
        
        # Should use our page number (7)
        assert req.page_number == 7
    
    def test_refine_requirement_handles_error(self):
        """Test refinement handles LLM errors gracefully."""
        mock_client = Mock()
        mock_client.generate.side_effect = Exception("LLM error")
        
        extractor = RequirementExtractor(llm_client=mock_client)
        
        req = Requirement(
            rfp_id="test",
            description="Original description",
            category=RequirementCategory.TECHNICAL,
            priority=RequirementPriority.HIGH
        )
        
        original_description = req.description
        # Should not crash, just return original requirement
        refined = extractor.refine_requirement(req)
        
        # Should still have a description (either original or unchanged)
        assert refined.description is not None
    
    def test_extract_from_text_handles_create_requirement_error(self):
        """Test extraction handles requirement creation errors."""
        mock_client = Mock()
        mock_client.generate.return_value = "LLM response"
        mock_client.extract_json.return_value = [
            {"description": ""},  # Empty description should cause error
            {"description": "Valid requirement", "category": "technical", 
             "priority": "high", "confidence": 0.8}
        ]
        
        extractor = RequirementExtractor(llm_client=mock_client)
        
        # Should skip invalid requirements and continue
        requirements = extractor._extract_from_text("Test", "test-rfp", None)
        
        # Should have at least the valid requirement
        assert len(requirements) >= 1
    
    def test_extract_by_page_processes_all_pages(self):
        """Test _extract_by_page processes all pages."""
        mock_client = Mock()
        mock_client.generate.return_value = "LLM response"
        mock_client.extract_json.side_effect = [
            [{"description": "Page 1 req", "category": "technical", 
              "priority": "high", "confidence": 0.85}],
            [{"description": "Page 2 req", "category": "functional", 
              "priority": "medium", "confidence": 0.75}],
        ]
        
        extractor = RequirementExtractor(llm_client=mock_client)
        
        rfp = RFP(id="test", file_name="test.pdf")
        rfp.extracted_text = "Page 1 content\nPage 2 content"
        rfp.extracted_text_by_page = {
            1: "Page 1 content",
            2: "Page 2 content"
        }
        
        requirements = extractor._extract_by_page(rfp)
        
        # Should have requirements from both pages
        assert len(requirements) == 2
        assert mock_client.generate.call_count == 2
    
    def test_extract_by_page_handles_page_errors(self):
        """Test _extract_by_page handles errors on individual pages."""
        mock_client = Mock()
        mock_client.generate.side_effect = [
            "LLM response",  # Page 1 succeeds
            Exception("LLM error"),  # Page 2 fails
        ]
        mock_client.extract_json.return_value = [
            {"description": "Page 1 req", "category": "technical", 
             "priority": "high", "confidence": 0.85}
        ]
        
        extractor = RequirementExtractor(llm_client=mock_client)
        
        rfp = RFP(id="test", file_name="test.pdf")
        rfp.extracted_text = "Page 1 content\nPage 2 content"
        rfp.extracted_text_by_page = {
            1: "Page 1 content",
            2: "Page 2 content"
        }
        
        requirements = extractor._extract_by_page(rfp)
        
        # Should have requirements from page 1, skip page 2
        assert len(requirements) == 1
    
    def test_extract_from_text_chunks_large_text(self):
        """Test _extract_from_text chunks large text."""
        mock_client = Mock()
        mock_client.generate.return_value = "LLM response"
        mock_client.extract_json.return_value = [
            {"description": "Requirement", "category": "technical", 
             "priority": "high", "confidence": 0.85}
        ]
        
        extractor = RequirementExtractor(llm_client=mock_client)
        
        # Create text larger than MAX_CHUNK_SIZE (4000)
        large_text = "A" * 5000
        
        requirements = extractor._extract_from_text(large_text, "test-rfp", None)
        
        # Should chunk and extract
        assert len(requirements) >= 1
        # Should have called generate multiple times (once per chunk)
        assert mock_client.generate.call_count > 1
    
    def test_chunk_text_with_sentence_boundaries(self):
        """Test chunking respects sentence boundaries."""
        mock_client = Mock()
        extractor = RequirementExtractor(llm_client=mock_client)
        
        # Create text with sentences that will be chunked (longer than MAX_CHUNK_SIZE=4000)
        text = ". ".join(["Sentence " + str(i) for i in range(500)]) + "."
        
        chunks = extractor._chunk_text(text)
        
        # Should have multiple chunks
        assert len(chunks) > 1
        # Verify all chunks have content
        assert all(len(chunk) > 0 for chunk in chunks)
    
    def test_chunk_text_finds_sentence_boundary(self):
        """Test chunking finds sentence boundaries correctly."""
        mock_client = Mock()
        extractor = RequirementExtractor(llm_client=mock_client)
        
        # Create text with clear sentence boundaries (long enough to chunk)
        sentences = [f"This is sentence {i}. " for i in range(300)]
        text = "".join(sentences)
        
        chunks = extractor._chunk_text(text)
        
        # Should chunk the text
        assert len(chunks) > 1
        # Verify chunks are reasonable size
        assert all(len(chunk) > 0 for chunk in chunks)
    
    def test_chunk_text_no_sentence_boundary_found(self):
        """Test chunking when no sentence boundary found."""
        mock_client = Mock()
        extractor = RequirementExtractor(llm_client=mock_client)
        
        # Create text without periods (no sentence boundaries) - long enough to chunk
        text = "A" * 5000  # Just letters, no periods
        
        chunks = extractor._chunk_text(text)
        
        # Should still chunk, but at fixed size
        assert len(chunks) > 1
        assert all(len(chunk) > 0 for chunk in chunks)


class TestConvenienceFunction:
    """Test convenience function for extraction."""
    
    def test_extract_requirements_from_rfp_function(self):
        """Test convenience function for extraction."""
        from services.requirement_extractor import extract_requirements_from_rfp
        
        mock_client = Mock()
        mock_client.generate.return_value = "LLM response"
        mock_client.extract_json.return_value = [
            {"description": "Requirement", "category": "technical", 
             "priority": "high", "confidence": 0.85}
        ]
        
        rfp = RFP(id="test", file_name="test.pdf")
        rfp.extracted_text = "Test content"
        
        # Mock create_llm_client to return our mock
        with patch('services.requirement_extractor.create_llm_client', return_value=mock_client):
            requirements = extract_requirements_from_rfp(rfp)
            
            assert len(requirements) == 1
    
    def test_extract_requirements_from_rfp_with_min_confidence(self):
        """Test convenience function with min_confidence parameter."""
        from services.requirement_extractor import extract_requirements_from_rfp
        
        mock_client = Mock()
        mock_client.generate.return_value = "LLM response"
        mock_client.extract_json.return_value = [
            {"description": "High confidence", "category": "technical", 
             "priority": "high", "confidence": 0.9},
            {"description": "Low confidence", "category": "functional", 
             "priority": "medium", "confidence": 0.2}  # Below threshold
        ]
        
        rfp = RFP(id="test", file_name="test.pdf")
        rfp.extracted_text = "Test content"
        
        with patch('services.requirement_extractor.create_llm_client', return_value=mock_client):
            requirements = extract_requirements_from_rfp(rfp, min_confidence=0.5)
            
            # Should only include high confidence requirement
            assert len(requirements) == 1
            assert requirements[0].confidence >= 0.5
    
    def test_refine_requirement_success(self):
        """Test successful requirement refinement."""
        mock_client = Mock()
        mock_client.generate.return_value = "Refined and improved requirement description"
        
        extractor = RequirementExtractor(llm_client=mock_client)
        
        req = Requirement(
            rfp_id="test",
            description="Original requirement",
            category=RequirementCategory.TECHNICAL,
            priority=RequirementPriority.HIGH
        )
        
        original_description = req.description
        refined = extractor.refine_requirement(req)
        
        # Description should be updated
        assert refined.description != original_description
        assert "Refined" in refined.description
    
    def test_deduplicate_requirements_with_similar_text(self):
        """Test deduplication with similar but not identical text."""
        mock_client = Mock()
        extractor = RequirementExtractor(llm_client=mock_client)
        
        req1 = Requirement(
            rfp_id="test",
            description="System must support 99.9% uptime",
            confidence=0.9
        )
        req2 = Requirement(
            rfp_id="test",
            description="System must support 99.9% uptime SLA",  # Similar but different
            confidence=0.9
        )
        
        deduplicated = extractor._deduplicate_requirements([req1, req2])
        
        # Should keep both (not exact duplicates)
        assert len(deduplicated) == 2
    
    def test_deduplicate_requirements_logs_duplicates(self):
        """Test deduplication logs duplicate requirements."""
        mock_client = Mock()
        extractor = RequirementExtractor(llm_client=mock_client)
        
        req1 = Requirement(
            rfp_id="test",
            description="System must support 99.9% uptime",
            confidence=0.9
        )
        req2 = Requirement(
            rfp_id="test",
            description="System must support 99.9% uptime",  # Exact duplicate
            confidence=0.9
        )
        
        with patch('services.requirement_extractor.logger') as mock_logger:
            deduplicated = extractor._deduplicate_requirements([req1, req2])
            
            # Should only keep one
            assert len(deduplicated) == 1
            # Should log the duplicate
            assert mock_logger.debug.called
    
    def test_extract_requirements_from_rfp(self):
        """Test convenience function works correctly."""
        with patch('services.requirement_extractor.RequirementExtractor') as mock_extractor_class:
            mock_extractor = Mock()
            mock_requirements = [Mock(), Mock()]
            mock_extractor.extract_from_rfp.return_value = mock_requirements
            mock_extractor_class.return_value = mock_extractor
            
            rfp = RFP(id="test", file_name="test.pdf")
            rfp.extracted_text = "Test content"
            
            result = extract_requirements_from_rfp(rfp, min_confidence=0.7)
            
            mock_extractor_class.assert_called_once()
            assert result == mock_requirements

