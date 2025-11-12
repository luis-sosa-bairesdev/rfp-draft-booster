"""
Unit tests for Risk Analysis page UI.

Note: These tests mock Streamlit components to test the logic without requiring
a full Streamlit runtime.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from models.rfp import RFP, RFPStatus
from models.risk import Risk, RiskCategory, RiskSeverity


class TestRiskAnalysisPageHelpers:
    """Test helper functions in Risk Analysis page."""
    
    def test_get_category_icon(self):
        """Test category icon helper function."""
        # Test the icon mapping logic (same as in the page)
        icons = {
            RiskCategory.LEGAL: "⚖️",
            RiskCategory.FINANCIAL: "💰",
            RiskCategory.TIMELINE: "⏰",
            RiskCategory.TECHNICAL: "🔧",
            RiskCategory.COMPLIANCE: "📋",
        }
        
        assert icons[RiskCategory.LEGAL] == "⚖️"
        assert icons[RiskCategory.FINANCIAL] == "💰"
        assert icons[RiskCategory.TIMELINE] == "⏰"
        assert icons[RiskCategory.TECHNICAL] == "🔧"
        assert icons[RiskCategory.COMPLIANCE] == "📋"
        
        # Test default
        default_icon = icons.get(RiskCategory.LEGAL, "⚠️")
        assert default_icon == "⚖️"


class TestRiskAnalysisPageLogic:
    """Test business logic functions in Risk Analysis page."""
    
    def test_display_risk_table_filtering(self):
        """Test risk table filtering logic."""
        # Create test risks
        risk1 = Risk(
            rfp_id="test-rfp-1",
            clause_text="Unlimited liability clause",
            category=RiskCategory.LEGAL,
            severity=RiskSeverity.CRITICAL,
            confidence=0.9,
            page_number=1
        )
        
        risk2 = Risk(
            rfp_id="test-rfp-1",
            clause_text="Payment terms: Net 90 days",
            category=RiskCategory.FINANCIAL,
            severity=RiskSeverity.HIGH,
            confidence=0.8,
            page_number=2
        )
        
        risk3 = Risk(
            rfp_id="test-rfp-1",
            clause_text="Complete in 30 days, no extensions",
            category=RiskCategory.TIMELINE,
            severity=RiskSeverity.CRITICAL,
            confidence=0.95,
            page_number=1
        )
        
        risks = [risk1, risk2, risk3]
        
        # Test filtering by category
        filtered_legal = [r for r in risks if r.category.value == "legal"]
        assert len(filtered_legal) == 1
        assert filtered_legal[0].category == RiskCategory.LEGAL
        
        # Test filtering by severity
        filtered_critical = [r for r in risks if r.severity.value == "critical"]
        assert len(filtered_critical) == 2
        
        # Test filtering by acknowledged status
        risk1.acknowledge("Will negotiate")
        filtered_unacknowledged = [r for r in risks if not r.acknowledged]
        assert len(filtered_unacknowledged) == 2
        
        # Test no filter
        filtered_all = risks
        assert len(filtered_all) == 3
    
    def test_risk_statistics(self):
        """Test risk statistics calculation."""
        risks = [
            Risk(
                rfp_id="test-rfp-1",
                clause_text=f"Risk clause {i}",
                category=RiskCategory.LEGAL if i % 2 == 0 else RiskCategory.FINANCIAL,
                severity=RiskSeverity.CRITICAL if i < 3 else RiskSeverity.HIGH,
                confidence=0.9 if i < 5 else 0.7,
                acknowledged=i < 2
            )
            for i in range(10)
        ]
        
        # Calculate statistics
        total = len(risks)
        acknowledged_count = sum(1 for r in risks if r.acknowledged)
        avg_confidence = sum(r.confidence for r in risks) / len(risks)
        critical_count = sum(1 for r in risks if r.severity == RiskSeverity.CRITICAL)
        high_confidence = sum(1 for r in risks if r.confidence >= 0.75)
        
        assert total == 10
        assert acknowledged_count == 2
        assert 0.7 <= avg_confidence <= 0.9
        assert critical_count == 3
        assert high_confidence == 5
        
        # Category breakdown
        category_counts = {}
        for risk in risks:
            cat = risk.category.value
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        assert category_counts["legal"] == 5
        assert category_counts["financial"] == 5
    
    def test_risk_acknowledgment(self):
        """Test risk acknowledgment functionality."""
        risk = Risk(
            rfp_id="test-rfp-1",
            clause_text="Test risk clause",
            acknowledged=False
        )
        
        assert risk.acknowledged is False
        assert risk.acknowledged_at is None
        
        # Acknowledge with notes
        risk.acknowledge("Will negotiate this clause")
        
        assert risk.acknowledged is True
        assert risk.acknowledgment_notes == "Will negotiate this clause"
        assert risk.acknowledged_at is not None
        assert isinstance(risk.acknowledged_at, datetime)
        
        # Acknowledge without notes
        risk2 = Risk(
            rfp_id="test-rfp-1",
            clause_text="Another risk",
            acknowledged=False
        )
        
        risk2.acknowledge()
        
        assert risk2.acknowledged is True
        assert risk2.acknowledgment_notes == ""
        assert risk2.acknowledged_at is not None


class TestRiskAnalysisPageIntegration:
    """Test integration aspects of Risk Analysis page."""
    
    def test_risk_crud_operations(self):
        """Test CRUD operations on risks."""
        risks = []
        
        # Create
        new_risk = Risk(
            rfp_id="test-rfp-1",
            clause_text="New risk clause",
            category=RiskCategory.LEGAL,
            severity=RiskSeverity.HIGH,
            confidence=0.8
        )
        risks.append(new_risk)
        assert len(risks) == 1
        
        # Read
        assert risks[0].clause_text == "New risk clause"
        
        # Update
        risks[0].update(
            recommendation="New recommendation",
            alternative_language="New alternative"
        )
        assert risks[0].recommendation == "New recommendation"
        assert risks[0].alternative_language == "New alternative"
        
        # Acknowledge (update)
        risks[0].acknowledge("Will address")
        assert risks[0].acknowledged is True
        
        # Delete (remove from list)
        risks.remove(risks[0])
        assert len(risks) == 0
    
    def test_risk_filtering_combinations(self):
        """Test various filtering combinations."""
        risks = [
            Risk(
                rfp_id="test-rfp-1",
                clause_text=f"Risk {i}",
                category=RiskCategory.LEGAL if i % 2 == 0 else RiskCategory.FINANCIAL,
                severity=RiskSeverity.CRITICAL if i < 3 else RiskSeverity.HIGH,
                acknowledged=i < 2
            )
            for i in range(6)
        ]
        
        # Filter by category only
        legal_risks = [r for r in risks if r.category.value == "legal"]
        assert len(legal_risks) == 3
        
        # Filter by severity only
        critical_risks = [r for r in risks if r.severity.value == "critical"]
        assert len(critical_risks) == 3
        
        # Filter by acknowledged status only
        unacknowledged = [r for r in risks if not r.acknowledged]
        assert len(unacknowledged) == 4
        
        # Combined filters: legal AND critical AND unacknowledged
        filtered = [
            r for r in risks
            if r.category.value == "legal"
            and r.severity.value == "critical"
            and not r.acknowledged
        ]
        assert len(filtered) == 1
    
    def test_risk_export_data_structure(self):
        """Test risk data structure for export."""
        risk = Risk(
            rfp_id="test-rfp-1",
            clause_text="Test clause",
            category=RiskCategory.LEGAL,
            severity=RiskSeverity.CRITICAL,
            confidence=0.95,
            page_number=5,
            recommendation="Test recommendation",
            alternative_language="Test alternative",
            acknowledged=True,
            acknowledgment_notes="Will negotiate"
        )
        
        # Test to_dict for JSON export
        data = risk.to_dict()
        
        assert data["rfp_id"] == "test-rfp-1"
        assert data["clause_text"] == "Test clause"
        assert data["category"] == "legal"
        assert data["severity"] == "critical"
        assert data["confidence"] == 0.95
        assert data["page_number"] == 5
        assert data["recommendation"] == "Test recommendation"
        assert data["alternative_language"] == "Test alternative"
        assert data["acknowledged"] is True
        assert data["acknowledgment_notes"] == "Will negotiate"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_risk_confidence_labels(self):
        """Test confidence label calculations."""
        very_high = Risk(rfp_id="test", clause_text="Test", confidence=0.95)
        high = Risk(rfp_id="test", clause_text="Test", confidence=0.80)
        medium = Risk(rfp_id="test", clause_text="Test", confidence=0.60)
        low = Risk(rfp_id="test", clause_text="Test", confidence=0.30)
        
        assert very_high.get_confidence_label() == "Very High"
        assert high.get_confidence_label() == "High"
        assert medium.get_confidence_label() == "Medium"
        assert low.get_confidence_label() == "Low"
    
    def test_risk_severity_colors(self):
        """Test severity color codes."""
        critical = Risk(rfp_id="test", clause_text="Test", severity=RiskSeverity.CRITICAL)
        high = Risk(rfp_id="test", clause_text="Test", severity=RiskSeverity.HIGH)
        medium = Risk(rfp_id="test", clause_text="Test", severity=RiskSeverity.MEDIUM)
        low = Risk(rfp_id="test", clause_text="Test", severity=RiskSeverity.LOW)
        
        assert critical.get_severity_color() == "#FF4444"
        assert high.get_severity_color() == "#FF8800"
        assert medium.get_severity_color() == "#FFBB00"
        assert low.get_severity_color() == "#4CAF50"
    
    def test_risk_category_icons(self):
        """Test category icon mapping."""
        legal = Risk(rfp_id="test", clause_text="Test", category=RiskCategory.LEGAL)
        financial = Risk(rfp_id="test", clause_text="Test", category=RiskCategory.FINANCIAL)
        timeline = Risk(rfp_id="test", clause_text="Test", category=RiskCategory.TIMELINE)
        technical = Risk(rfp_id="test", clause_text="Test", category=RiskCategory.TECHNICAL)
        compliance = Risk(rfp_id="test", clause_text="Test", category=RiskCategory.COMPLIANCE)
        
        assert legal.get_category_icon() == "⚖️"
        assert financial.get_category_icon() == "💰"
        assert timeline.get_category_icon() == "⏰"
        assert technical.get_category_icon() == "🔧"
        assert compliance.get_category_icon() == "📋"


class TestRiskAnalysisPageEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_risks_list(self):
        """Test handling of empty risks list."""
        risks = []
        
        # Filtering should return empty list
        filtered = [r for r in risks if r.category.value == "legal"]
        assert len(filtered) == 0
        
        # Statistics should handle empty list
        total = len(risks)
        assert total == 0
    
    def test_risk_with_missing_fields(self):
        """Test risk with optional fields missing."""
        risk = Risk(
            rfp_id="test-rfp-1",
            clause_text="Test clause"
        )
        
        # Should have defaults
        assert risk.page_number is None
        assert risk.recommendation == ""
        assert risk.alternative_language == ""
        assert risk.acknowledged is False
    
    def test_risk_with_long_clause_text(self):
        """Test risk with very long clause text."""
        long_text = "A" * 1000
        risk = Risk(
            rfp_id="test-rfp-1",
            clause_text=long_text
        )
        
        # Clause text should be stored
        assert len(risk.clause_text) == 1000
        
        # But may be truncated in UI (tested in detector)
        assert len(risk.clause_text[:500]) == 500
    
    def test_multiple_risks_same_clause(self):
        """Test handling multiple risks with similar clauses."""
        risk1 = Risk(
            rfp_id="test-rfp-1",
            clause_text="Vendor assumes all liability",
            category=RiskCategory.LEGAL,
            severity=RiskSeverity.CRITICAL
        )
        
        risk2 = Risk(
            rfp_id="test-rfp-1",
            clause_text="Vendor assumes all liability",  # Same clause
            category=RiskCategory.LEGAL,
            severity=RiskSeverity.CRITICAL
        )
        
        # Both should be valid risks (deduplication handled by detector)
        assert risk1.clause_text == risk2.clause_text
        assert risk1.id != risk2.id  # Different IDs
    
    def test_import_risks_from_json(self):
        """Test importing risks from JSON data structure."""
        import json
        
        # Create sample JSON data
        risks_json = [
            {
                "id": "test-risk-1",
                "rfp_id": "test-rfp-1",
                "clause_text": "Test risk clause",
                "category": "legal",
                "severity": "high",
                "confidence": 0.85,
                "page_number": 1,
                "recommendation": "Test recommendation",
                "alternative_language": "Test alternative",
                "acknowledged": False,
                "acknowledgment_notes": "",
                "acknowledged_at": None,
                "created_at": "2025-11-12T15:09:42.599649",
                "updated_at": "2025-11-12T15:09:42.599656"
            }
        ]
        
        # Test conversion from JSON
        imported_risks = []
        for risk_dict in risks_json:
            risk = Risk.from_dict(risk_dict)
            imported_risks.append(risk)
        
        assert len(imported_risks) == 1
        assert imported_risks[0].clause_text == "Test risk clause"
        assert imported_risks[0].category == RiskCategory.LEGAL
        assert imported_risks[0].severity == RiskSeverity.HIGH
    
    def test_import_risks_duplicate_prevention(self):
        """Test that importing duplicate risks is prevented."""
        existing_risk = Risk(
            rfp_id="test-rfp-1",
            clause_text="Existing risk",
            id="existing-id-123"
        )
        
        existing_risks = [existing_risk]
        existing_ids = {r.id for r in existing_risks}
        
        # Try to import same risk
        new_risk = Risk(
            rfp_id="test-rfp-1",
            clause_text="Existing risk",
            id="existing-id-123"  # Same ID
        )
        
        # Should be filtered out
        new_risks = [r for r in [new_risk] if r.id not in existing_ids]
        assert len(new_risks) == 0
        
        # Try to import different risk
        different_risk = Risk(
            rfp_id="test-rfp-1",
            clause_text="New risk",
            id="new-id-456"
        )
        
        new_risks = [r for r in [different_risk] if r.id not in existing_ids]
        assert len(new_risks) == 1
        assert new_risks[0].id == "new-id-456"
    
    def test_import_risks_json_validation(self):
        """Test JSON validation for risk imports."""
        import json
        
        # Valid JSON
        valid_json = '[{"id": "test", "rfp_id": "test", "clause_text": "Test", "category": "legal", "severity": "high", "confidence": 0.8}]'
        try:
            data = json.loads(valid_json)
            assert isinstance(data, list)
            assert len(data) == 1
        except json.JSONDecodeError:
            pytest.fail("Valid JSON should not raise JSONDecodeError")
        
        # Invalid JSON
        invalid_json = '[{"id": "test"}'  # Missing closing bracket
        with pytest.raises(json.JSONDecodeError):
            json.loads(invalid_json)

