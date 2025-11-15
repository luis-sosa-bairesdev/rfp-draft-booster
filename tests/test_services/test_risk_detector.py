"""
Unit tests for Risk Detector.

Tests cover:
- Risk detection from RFP text
- Pattern-based detection
- AI-powered detection
- Page-by-page detection
- Text chunking for large documents
- Deduplication logic
- Confidence filtering
- Error handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from models import RFP, RFPStatus, Risk, RiskCategory, RiskSeverity
from services.risk_detector import RiskDetector, detect_risks_from_rfp


class TestRiskDetector:
    """Test RiskDetector service."""
    
    def test_initialization(self):
        """Test detector initialization."""
        mock_client = Mock()
        detector = RiskDetector(
            llm_client=mock_client,
            min_confidence=0.5,
            use_patterns=True,
            use_ai=True
        )
        
        assert detector.llm_client == mock_client
        assert detector.min_confidence == 0.5
        assert detector.use_patterns is True
        assert detector.use_ai is True
    
    def test_initialization_with_defaults(self):
        """Test detector uses default client if not provided."""
        with patch('services.risk_detector.create_llm_client') as mock_create:
            mock_client = Mock()
            mock_create.return_value = mock_client
            
            detector = RiskDetector(use_ai=True)
            
            assert detector.llm_client == mock_client
            assert detector.min_confidence == 0.3
            assert detector.use_patterns is True
            assert detector.use_ai is True
            mock_create.assert_called_once_with(fallback=True)
    
    def test_initialization_patterns_only(self):
        """Test detector can work with patterns only (no LLM)."""
        detector = RiskDetector(use_patterns=True, use_ai=False)
        
        assert detector.llm_client is None
        assert detector.use_patterns is True
        assert detector.use_ai is False
    
    def test_detect_from_rfp_no_text_raises_error(self):
        """Test error when RFP has no extracted text."""
        detector = RiskDetector(use_patterns=True, use_ai=False)
        
        rfp = RFP(id="test", file_name="test.pdf")
        rfp.extracted_text = None
        
        with pytest.raises(ValueError, match="RFP must have extracted_text"):
            detector.detect_from_rfp(rfp)
    
    def test_pattern_detection_legal_risks(self):
        """Test pattern detection for legal risks."""
        detector = RiskDetector(use_patterns=True, use_ai=False)
        
        rfp = RFP(id="test-rfp", file_name="test.pdf")
        rfp.extracted_text = "Vendor assumes all liability for any damages."
        
        risks = detector.detect_from_rfp(rfp)
        
        assert len(risks) > 0
        legal_risks = [r for r in risks if r.category == RiskCategory.LEGAL]
        assert len(legal_risks) > 0
        # Check that at least one legal risk mentions liability or assumes all risk
        assert any("liability" in r.clause_text.lower() or "assumes all risk" in r.clause_text.lower() for r in legal_risks)
    
    def test_pattern_detection_financial_risks(self):
        """Test pattern detection for financial risks."""
        detector = RiskDetector(use_patterns=True, use_ai=False)
        
        rfp = RFP(id="test-rfp", file_name="test.pdf")
        rfp.extracted_text = "Payment terms: Net 90 days from invoice date."
        
        risks = detector.detect_from_rfp(rfp)
        
        assert len(risks) > 0
        financial_risks = [r for r in risks if r.category == RiskCategory.FINANCIAL]
        assert len(financial_risks) > 0
    
    def test_pattern_detection_timeline_risks(self):
        """Test pattern detection for timeline risks."""
        detector = RiskDetector(use_patterns=True, use_ai=False)
        
        rfp = RFP(id="test-rfp", file_name="test.pdf")
        rfp.extracted_text = "Project must be completed within 30 days. No extensions permitted."
        
        risks = detector.detect_from_rfp(rfp)
        
        assert len(risks) > 0
        timeline_risks = [r for r in risks if r.category == RiskCategory.TIMELINE]
        assert len(timeline_risks) > 0
    
    def test_ai_detection_from_simple_text(self):
        """Test AI detection from simple RFP text."""
        mock_client = Mock()
        mock_client.generate.return_value = "LLM response"
        mock_client.extract_json.return_value = [
            {
                "clause_text": "Vendor shall be liable for all damages",
                "category": "legal",
                "severity": "critical",
                "confidence": 0.95,
                "page_number": 1,
                "recommendation": "Negotiate liability cap",
                "alternative_language": "Limited liability clause"
            },
            {
                "clause_text": "Payment terms: Net 90 days",
                "category": "financial",
                "severity": "high",
                "confidence": 0.85,
                "page_number": 2,
                "recommendation": "Negotiate Net 30",
                "alternative_language": "Payment terms: Net 30 days"
            }
        ]
        
        detector = RiskDetector(
            llm_client=mock_client,
            use_patterns=False,
            use_ai=True,
            min_confidence=0.5
        )
        
        rfp = RFP(id="test-rfp", file_name="test.pdf")
        rfp.extracted_text = "Vendor liability clause. Payment terms."
        
        risks = detector.detect_from_rfp(rfp)
        
        assert len(risks) == 2
        assert risks[0].clause_text == "Vendor shall be liable for all damages"
        assert risks[0].category == RiskCategory.LEGAL
        assert risks[0].severity == RiskSeverity.CRITICAL
        assert risks[0].confidence == 0.95
        assert risks[0].recommendation == "Negotiate liability cap"
        assert risks[0].alternative_language == "Limited liability clause"
        assert risks[1].category == RiskCategory.FINANCIAL
    
    def test_combined_pattern_and_ai_detection(self):
        """Test combining pattern and AI detection."""
        mock_client = Mock()
        mock_client.generate.return_value = "LLM response"
        mock_client.extract_json.return_value = [
            {
                "clause_text": "Complex risk clause",
                "category": "legal",
                "severity": "high",
                "confidence": 0.80,
                "recommendation": "Review clause",
                "alternative_language": "Safer clause"
            }
        ]
        
        detector = RiskDetector(
            llm_client=mock_client,
            use_patterns=True,
            use_ai=True
        )
        
        rfp = RFP(id="test-rfp", file_name="test.pdf")
        rfp.extracted_text = "Vendor assumes all liability. Complex risk clause here."
        
        risks = detector.detect_from_rfp(rfp)
        
        # Should have risks from both pattern and AI
        assert len(risks) >= 1
    
    def test_detect_with_confidence_filtering(self):
        """Test risks below min_confidence are filtered out."""
        mock_client = Mock()
        mock_client.generate.return_value = "LLM response"
        mock_client.extract_json.return_value = [
            {
                "clause_text": "High confidence risk",
                "category": "legal",
                "severity": "high",
                "confidence": 0.90,
                "recommendation": "Test",
                "alternative_language": "Test"
            },
            {
                "clause_text": "Low confidence risk",
                "category": "financial",
                "severity": "medium",
                "confidence": 0.20,
                "recommendation": "Test",
                "alternative_language": "Test"
            },
            {
                "clause_text": "Medium confidence risk",
                "category": "timeline",
                "severity": "high",
                "confidence": 0.60,
                "recommendation": "Test",
                "alternative_language": "Test"
            }
        ]
        
        detector = RiskDetector(
            llm_client=mock_client,
            use_patterns=False,
            use_ai=True,
            min_confidence=0.5
        )
        
        rfp = RFP(id="test", file_name="test.pdf")
        rfp.extracted_text = "Test risks"
        
        risks = detector.detect_from_rfp(rfp)
        
        # Only 2 risks should pass (confidence >= 0.5)
        assert len(risks) == 2
        assert all(risk.confidence >= 0.5 for risk in risks)
    
    def test_detect_by_page(self):
        """Test detection page by page."""
        mock_client = Mock()
        mock_client.generate.return_value = "LLM response"
        mock_client.extract_json.side_effect = [
            [{
                "clause_text": "Risk from page 1",
                "category": "legal",
                "severity": "high",
                "confidence": 0.85,
                "recommendation": "Test",
                "alternative_language": "Test"
            }],
            [{
                "clause_text": "Risk from page 2",
                "category": "financial",
                "severity": "medium",
                "confidence": 0.75,
                "recommendation": "Test",
                "alternative_language": "Test"
            }],
        ]
        
        detector = RiskDetector(
            llm_client=mock_client,
            use_patterns=False,
            use_ai=True
        )
        
        rfp = RFP(id="test", file_name="test.pdf")
        rfp.extracted_text = "Page 1 content\nPage 2 content"
        rfp.extracted_text_by_page = {
            1: "Page 1 content",
            2: "Page 2 content"
        }
        
        risks = detector.detect_from_rfp(rfp)
        
        assert len(risks) == 2
        # Verify both pages were processed
        assert mock_client.generate.call_count == 2
    
    def test_deduplication(self):
        """Test duplicate risks are removed."""
        mock_client = Mock()
        mock_client.generate.return_value = "LLM response"
        mock_client.extract_json.side_effect = [
            [{
                "clause_text": "Vendor assumes all liability",
                "category": "legal",
                "severity": "critical",
                "confidence": 0.95,
                "recommendation": "Test",
                "alternative_language": "Test"
            }],
            [{
                "clause_text": "Vendor assumes all liability",  # Duplicate
                "category": "legal",
                "severity": "critical",
                "confidence": 0.95,
                "recommendation": "Test",
                "alternative_language": "Test"
            }],
        ]
        
        detector = RiskDetector(
            llm_client=mock_client,
            use_patterns=False,
            use_ai=True
        )
        
        rfp = RFP(id="test", file_name="test.pdf")
        rfp.extracted_text = "Page 1 content\nPage 2 content"
        rfp.extracted_text_by_page = {
            1: "Page 1 content",
            2: "Page 2 content"
        }
        
        risks = detector.detect_from_rfp(rfp)
        
        # Only 1 unique risk (duplicates removed)
        assert len(risks) == 1
    
    def test_text_chunking(self):
        """Test large text is chunked properly."""
        mock_client = Mock()
        detector = RiskDetector(
            llm_client=mock_client,
            use_patterns=False,
            use_ai=True
        )
        
        # Create text larger than MAX_CHUNK_SIZE
        large_text = "A" * 5000  # 5000 characters
        chunks = detector._chunk_text(large_text)
        
        assert len(chunks) > 1
        # Check chunks overlap
        assert len(chunks[0]) <= 4000  # MAX_CHUNK_SIZE from prompt_templates
    
    def test_create_risk_from_data(self):
        """Test creating Risk from LLM response data."""
        mock_client = Mock()
        detector = RiskDetector(llm_client=mock_client, use_patterns=False, use_ai=True)
        
        data = {
            "clause_text": "Unlimited liability clause",
            "category": "legal",
            "severity": "critical",
            "confidence": 0.98,
            "page_number": 5,
            "recommendation": "Negotiate liability cap",
            "alternative_language": "Limited liability clause"
        }
        
        risk = detector._create_risk(data, "test-rfp-1", None)
        
        assert risk.rfp_id == "test-rfp-1"
        assert risk.clause_text == "Unlimited liability clause"
        assert risk.category == RiskCategory.LEGAL
        assert risk.severity == RiskSeverity.CRITICAL
        assert risk.confidence == 0.98
        assert risk.page_number == 5
        assert risk.recommendation == "Negotiate liability cap"
        assert risk.alternative_language == "Limited liability clause"
    
    def test_create_risk_with_invalid_category(self):
        """Test invalid category defaults to legal."""
        mock_client = Mock()
        detector = RiskDetector(llm_client=mock_client, use_patterns=False, use_ai=True)
        
        data = {
            "clause_text": "Test",
            "category": "invalid_category",
            "severity": "high",
            "confidence": 0.8,
            "recommendation": "Test",
            "alternative_language": "Test"
        }
        
        risk = detector._create_risk(data, "test-rfp", None)
        
        assert risk.category == RiskCategory.LEGAL
    
    def test_create_risk_with_invalid_severity(self):
        """Test invalid severity defaults to medium."""
        mock_client = Mock()
        detector = RiskDetector(llm_client=mock_client, use_patterns=False, use_ai=True)
        
        data = {
            "clause_text": "Test",
            "category": "legal",
            "severity": "invalid_severity",
            "confidence": 0.8,
            "recommendation": "Test",
            "alternative_language": "Test"
        }
        
        risk = detector._create_risk(data, "test-rfp", None)
        
        assert risk.severity == RiskSeverity.MEDIUM
    
    def test_create_risk_clamps_confidence(self):
        """Test confidence is clamped to valid range."""
        mock_client = Mock()
        detector = RiskDetector(llm_client=mock_client, use_patterns=False, use_ai=True)
        
        # Test confidence > 1.0
        data = {
            "clause_text": "Test",
            "category": "legal",
            "severity": "high",
            "confidence": 1.5,
            "recommendation": "Test",
            "alternative_language": "Test"
        }
        
        risk = detector._create_risk(data, "test-rfp", None)
        assert risk.confidence == 1.0
        
        # Test confidence < 0.0
        data["confidence"] = -0.5
        risk = detector._create_risk(data, "test-rfp", None)
        assert risk.confidence == 0.0
    
    def test_create_risk_missing_clause_text_raises_error(self):
        """Test missing clause_text raises ValueError."""
        mock_client = Mock()
        detector = RiskDetector(llm_client=mock_client, use_patterns=False, use_ai=True)
        
        data = {
            "category": "legal",
            "severity": "high",
            "confidence": 0.8,
            "recommendation": "Test",
            "alternative_language": "Test"
        }
        
        with pytest.raises(ValueError, match="Risk must have clause_text"):
            detector._create_risk(data, "test-rfp", None)
    
    def test_create_risk_empty_clause_text_raises_error(self):
        """Test empty clause_text raises ValueError."""
        mock_client = Mock()
        detector = RiskDetector(llm_client=mock_client, use_patterns=False, use_ai=True)
        
        data = {
            "clause_text": "   ",
            "category": "legal",
            "severity": "high",
            "confidence": 0.8,
            "recommendation": "Test",
            "alternative_language": "Test"
        }
        
        with pytest.raises(ValueError, match="Risk must have clause_text"):
            detector._create_risk(data, "test-rfp", None)
    
    def test_create_risk_prefers_llm_page_number(self):
        """Test LLM's page_number is preferred over provided page_number."""
        mock_client = Mock()
        detector = RiskDetector(llm_client=mock_client, use_patterns=False, use_ai=True)
        
        data = {
            "clause_text": "Test",
            "category": "legal",
            "severity": "high",
            "confidence": 0.8,
            "page_number": 10,  # LLM's page number
            "recommendation": "Test",
            "alternative_language": "Test"
        }
        
        risk = detector._create_risk(data, "test-rfp", 5)  # Provided page number
        
        assert risk.page_number == 10  # LLM's page number is used
    
    def test_empty_page_text_skipped(self):
        """Test empty pages are skipped during detection."""
        mock_client = Mock()
        mock_client.generate.return_value = "LLM response"
        mock_client.extract_json.return_value = [{
            "clause_text": "Risk",
            "category": "legal",
            "severity": "high",
            "confidence": 0.85,
            "recommendation": "Test",
            "alternative_language": "Test"
        }]
        
        detector = RiskDetector(
            llm_client=mock_client,
            use_patterns=False,
            use_ai=True
        )
        
        rfp = RFP(id="test", file_name="test.pdf")
        rfp.extracted_text = "Page 1 with content"
        rfp.extracted_text_by_page = {
            1: "Page 1 with content",
            2: "   ",  # Empty page (only whitespace)
            3: "",    # Empty page
        }
        
        risks = detector.detect_from_rfp(rfp)
        
        # Only page 1 should be processed
        assert mock_client.generate.call_count == 1
    
    def test_error_handling_in_ai_detection(self):
        """Test errors during AI detection are handled gracefully."""
        mock_client = Mock()
        mock_client.generate.side_effect = Exception("LLM error")
        
        detector = RiskDetector(
            llm_client=mock_client,
            use_patterns=False,
            use_ai=True
        )
        
        rfp = RFP(id="test", file_name="test.pdf")
        rfp.extracted_text = "Test text"
        
        # Should not raise, but return empty list
        risks = detector.detect_from_rfp(rfp)
        assert risks == []
    
    def test_error_handling_in_create_risk(self):
        """Test errors during risk creation are handled gracefully."""
        mock_client = Mock()
        mock_client.generate.return_value = "LLM response"
        mock_client.extract_json.return_value = [
            {
                "clause_text": "Valid risk",
                "category": "legal",
                "severity": "high",
                "confidence": 0.8,
                "recommendation": "Test",
                "alternative_language": "Test"
            },
            {
                # Invalid risk (missing clause_text)
                "category": "legal",
                "severity": "high",
                "confidence": 0.8
            }
        ]
        
        detector = RiskDetector(
            llm_client=mock_client,
            use_patterns=False,
            use_ai=True
        )
        
        rfp = RFP(id="test", file_name="test.pdf")
        rfp.extracted_text = "Test text"
        
        # Should only return valid risks
        risks = detector.detect_from_rfp(rfp)
        assert len(risks) == 1
        assert risks[0].clause_text == "Valid risk"
    
    def test_convenience_function(self):
        """Test detect_risks_from_rfp convenience function."""
        mock_client = Mock()
        mock_client.generate.return_value = "LLM response"
        mock_client.extract_json.return_value = [{
            "clause_text": "Test risk",
            "category": "legal",
            "severity": "high",
            "confidence": 0.8,
            "recommendation": "Test",
            "alternative_language": "Test"
        }]
        
        rfp = RFP(id="test", file_name="test.pdf")
        rfp.extracted_text = "Test text"
        
        risks = detect_risks_from_rfp(
            rfp,
            llm_client=mock_client,
            use_patterns=False,
            use_ai=True
        )
        
        assert len(risks) == 1
        assert risks[0].clause_text == "Test risk"
    
    def test_pattern_detection_with_page_numbers(self):
        """Test pattern detection extracts page numbers when available."""
        detector = RiskDetector(use_patterns=True, use_ai=False)
        
        rfp = RFP(id="test-rfp", file_name="test.pdf")
        rfp.extracted_text = "Vendor assumes all liability."
        rfp.extracted_text_by_page = {
            1: "Some text.",
            2: "Vendor assumes all liability.",
            3: "More text."
        }
        
        risks = detector.detect_from_rfp(rfp)
        
        # Should have detected risks with page numbers
        assert len(risks) > 0
        risks_with_pages = [r for r in risks if r.page_number is not None]
        assert len(risks_with_pages) > 0

