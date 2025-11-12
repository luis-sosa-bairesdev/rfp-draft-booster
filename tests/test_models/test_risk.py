"""
Unit tests for Risk model.

Tests cover:
- Risk creation and validation
- Category and severity enums
- Confidence scoring
- Page number validation
- Serialization (to_dict/from_dict)
- Helper methods (colors, icons, labels)
- Acknowledgment functionality
"""

import pytest
from datetime import datetime
from models.risk import (
    Risk,
    RiskCategory,
    RiskSeverity,
    get_category_display_names,
    get_severity_display_names,
)


class TestRiskModel:
    """Test Risk data model."""
    
    def test_create_risk_with_defaults(self):
        """Test creating a risk with default values."""
        risk = Risk(
            rfp_id="test-rfp-1",
            clause_text="Vendor assumes all liability"
        )
        
        assert risk.rfp_id == "test-rfp-1"
        assert risk.clause_text == "Vendor assumes all liability"
        assert risk.category == RiskCategory.LEGAL
        assert risk.severity == RiskSeverity.MEDIUM
        assert risk.confidence == 0.0
        assert risk.page_number is None
        assert risk.recommendation == ""
        assert risk.alternative_language == ""
        assert risk.acknowledged is False
        assert risk.acknowledgment_notes == ""
        assert risk.acknowledged_at is None
        assert isinstance(risk.id, str)
        assert len(risk.id) > 0
    
    def test_create_risk_with_all_fields(self):
        """Test creating a risk with all fields specified."""
        risk = Risk(
            rfp_id="test-rfp-1",
            clause_text="Unlimited liability clause",
            category=RiskCategory.LEGAL,
            severity=RiskSeverity.CRITICAL,
            confidence=0.95,
            page_number=12,
            recommendation="Negotiate liability cap",
            alternative_language="Limited liability clause",
            acknowledged=True,
            acknowledgment_notes="Will negotiate",
            acknowledged_at=datetime.now()
        )
        
        assert risk.category == RiskCategory.LEGAL
        assert risk.severity == RiskSeverity.CRITICAL
        assert risk.confidence == 0.95
        assert risk.page_number == 12
        assert risk.recommendation == "Negotiate liability cap"
        assert risk.alternative_language == "Limited liability clause"
        assert risk.acknowledged is True
        assert risk.acknowledgment_notes == "Will negotiate"
        assert risk.acknowledged_at is not None
    
    def test_confidence_validation_min(self):
        """Test confidence cannot be less than 0.0."""
        with pytest.raises(ValueError, match="Confidence must be between 0.0 and 1.0"):
            Risk(
                rfp_id="test",
                clause_text="Test",
                confidence=-0.1
            )
    
    def test_confidence_validation_max(self):
        """Test confidence cannot be greater than 1.0."""
        with pytest.raises(ValueError, match="Confidence must be between 0.0 and 1.0"):
            Risk(
                rfp_id="test",
                clause_text="Test",
                confidence=1.1
            )
    
    def test_page_number_validation(self):
        """Test page number must be positive."""
        with pytest.raises(ValueError, match="Page number must be >= 1"):
            Risk(
                rfp_id="test",
                clause_text="Test",
                page_number=0
            )
    
    def test_category_from_string(self):
        """Test category can be created from string."""
        risk = Risk(
            rfp_id="test",
            clause_text="Test",
            category="financial"
        )
        assert risk.category == RiskCategory.FINANCIAL
    
    def test_severity_from_string(self):
        """Test severity can be created from string."""
        risk = Risk(
            rfp_id="test",
            clause_text="Test",
            severity="high"
        )
        assert risk.severity == RiskSeverity.HIGH
    
    def test_to_dict(self):
        """Test serialization to dictionary."""
        risk = Risk(
            rfp_id="test-rfp-1",
            clause_text="Test risk clause",
            category=RiskCategory.FINANCIAL,
            severity=RiskSeverity.HIGH,
            confidence=0.85,
            page_number=5,
            recommendation="Test recommendation",
            alternative_language="Test alternative"
        )
        
        data = risk.to_dict()
        
        assert data["rfp_id"] == "test-rfp-1"
        assert data["clause_text"] == "Test risk clause"
        assert data["category"] == "financial"
        assert data["severity"] == "high"
        assert data["confidence"] == 0.85
        assert data["page_number"] == 5
        assert data["recommendation"] == "Test recommendation"
        assert data["alternative_language"] == "Test alternative"
        assert data["acknowledged"] is False
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_to_dict_with_acknowledgment(self):
        """Test serialization includes acknowledgment data."""
        risk = Risk(
            rfp_id="test",
            clause_text="Test",
            acknowledged=True,
            acknowledgment_notes="Will address",
            acknowledged_at=datetime.now()
        )
        
        data = risk.to_dict()
        
        assert data["acknowledged"] is True
        assert data["acknowledgment_notes"] == "Will address"
        assert data["acknowledged_at"] is not None
    
    def test_from_dict(self):
        """Test deserialization from dictionary."""
        data = {
            "id": "test-id-123",
            "rfp_id": "test-rfp-1",
            "clause_text": "Test risk clause",
            "category": "timeline",
            "severity": "critical",
            "confidence": 0.90,
            "page_number": 7,
            "recommendation": "Test recommendation",
            "alternative_language": "Test alternative",
            "acknowledged": True,
            "acknowledgment_notes": "Will negotiate",
            "acknowledged_at": "2025-11-10T12:00:00",
            "created_at": "2025-11-10T12:00:00",
            "updated_at": "2025-11-10T12:00:00"
        }
        
        risk = Risk.from_dict(data)
        
        assert risk.id == "test-id-123"
        assert risk.rfp_id == "test-rfp-1"
        assert risk.clause_text == "Test risk clause"
        assert risk.category == RiskCategory.TIMELINE
        assert risk.severity == RiskSeverity.CRITICAL
        assert risk.confidence == 0.90
        assert risk.page_number == 7
        assert risk.recommendation == "Test recommendation"
        assert risk.alternative_language == "Test alternative"
        assert risk.acknowledged is True
        assert risk.acknowledgment_notes == "Will negotiate"
        assert isinstance(risk.acknowledged_at, datetime)
    
    def test_from_dict_without_acknowledgment(self):
        """Test deserialization when acknowledgment is None."""
        data = {
            "id": "test-id",
            "rfp_id": "test",
            "clause_text": "Test",
            "category": "legal",
            "severity": "medium",
            "confidence": 0.5,
            "acknowledged": False,
            "acknowledged_at": None,
            "created_at": "2025-11-10T12:00:00",
            "updated_at": "2025-11-10T12:00:00"
        }
        
        risk = Risk.from_dict(data)
        
        assert risk.acknowledged is False
        assert risk.acknowledged_at is None
    
    def test_update_method(self):
        """Test updating risk fields."""
        risk = Risk(
            rfp_id="test",
            clause_text="Original",
            acknowledged=False
        )
        
        original_updated_at = risk.updated_at
        
        risk.update(
            clause_text="Updated clause",
            recommendation="New recommendation",
            acknowledged=True
        )
        
        assert risk.clause_text == "Updated clause"
        assert risk.recommendation == "New recommendation"
        assert risk.acknowledged is True
        assert risk.updated_at > original_updated_at
    
    def test_acknowledge_method(self):
        """Test acknowledging a risk."""
        risk = Risk(
            rfp_id="test",
            clause_text="Test",
            acknowledged=False
        )
        
        original_updated_at = risk.updated_at
        
        risk.acknowledge("Will negotiate this clause")
        
        assert risk.acknowledged is True
        assert risk.acknowledgment_notes == "Will negotiate this clause"
        assert risk.acknowledged_at is not None
        assert risk.updated_at > original_updated_at
    
    def test_acknowledge_without_notes(self):
        """Test acknowledging a risk without notes."""
        risk = Risk(
            rfp_id="test",
            clause_text="Test",
            acknowledged=False
        )
        
        risk.acknowledge()
        
        assert risk.acknowledged is True
        assert risk.acknowledgment_notes == ""
        assert risk.acknowledged_at is not None
    
    def test_get_confidence_label_very_high(self):
        """Test confidence label for very high confidence."""
        risk = Risk(rfp_id="test", clause_text="Test", confidence=0.95)
        assert risk.get_confidence_label() == "Very High"
    
    def test_get_confidence_label_high(self):
        """Test confidence label for high confidence."""
        risk = Risk(rfp_id="test", clause_text="Test", confidence=0.80)
        assert risk.get_confidence_label() == "High"
    
    def test_get_confidence_label_medium(self):
        """Test confidence label for medium confidence."""
        risk = Risk(rfp_id="test", clause_text="Test", confidence=0.60)
        assert risk.get_confidence_label() == "Medium"
    
    def test_get_confidence_label_low(self):
        """Test confidence label for low confidence."""
        risk = Risk(rfp_id="test", clause_text="Test", confidence=0.30)
        assert risk.get_confidence_label() == "Low"
    
    def test_get_severity_color(self):
        """Test severity colors for UI."""
        risk_critical = Risk(rfp_id="test", clause_text="Test", severity=RiskSeverity.CRITICAL)
        risk_high = Risk(rfp_id="test", clause_text="Test", severity=RiskSeverity.HIGH)
        risk_medium = Risk(rfp_id="test", clause_text="Test", severity=RiskSeverity.MEDIUM)
        risk_low = Risk(rfp_id="test", clause_text="Test", severity=RiskSeverity.LOW)
        
        assert risk_critical.get_severity_color() == "#FF4444"
        assert risk_high.get_severity_color() == "#FF8800"
        assert risk_medium.get_severity_color() == "#FFBB00"
        assert risk_low.get_severity_color() == "#4CAF50"
    
    def test_get_category_icon(self):
        """Test category icons for UI."""
        categories_icons = {
            RiskCategory.LEGAL: "⚖️",
            RiskCategory.FINANCIAL: "💰",
            RiskCategory.TIMELINE: "⏰",
            RiskCategory.TECHNICAL: "🔧",
            RiskCategory.COMPLIANCE: "📋",
        }
        
        for category, expected_icon in categories_icons.items():
            risk = Risk(rfp_id="test", clause_text="Test", category=category)
            assert risk.get_category_icon() == expected_icon


class TestRiskEnums:
    """Test risk enums and helper functions."""
    
    def test_risk_category_values(self):
        """Test all RiskCategory values."""
        assert RiskCategory.LEGAL.value == "legal"
        assert RiskCategory.FINANCIAL.value == "financial"
        assert RiskCategory.TIMELINE.value == "timeline"
        assert RiskCategory.TECHNICAL.value == "technical"
        assert RiskCategory.COMPLIANCE.value == "compliance"
    
    def test_risk_severity_values(self):
        """Test all RiskSeverity values."""
        assert RiskSeverity.CRITICAL.value == "critical"
        assert RiskSeverity.HIGH.value == "high"
        assert RiskSeverity.MEDIUM.value == "medium"
        assert RiskSeverity.LOW.value == "low"
    
    def test_get_category_display_names(self):
        """Test category display names helper."""
        names = get_category_display_names()
        
        assert names["legal"] == "Legal"
        assert names["financial"] == "Financial"
        assert names["timeline"] == "Timeline"
        assert names["technical"] == "Technical"
        assert names["compliance"] == "Compliance"
        assert len(names) == 5
    
    def test_get_severity_display_names(self):
        """Test severity display names helper."""
        names = get_severity_display_names()
        
        assert names["critical"] == "Critical"
        assert names["high"] == "High"
        assert names["medium"] == "Medium"
        assert names["low"] == "Low"
        assert len(names) == 4

