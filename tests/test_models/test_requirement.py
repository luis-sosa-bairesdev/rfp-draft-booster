"""
Unit tests for Requirement model.

Tests cover:
- Requirement creation and validation
- Category and priority enums
- Confidence scoring
- Page number validation
- Serialization (to_dict/from_dict)
- Helper methods (colors, icons, labels)
- Update functionality
"""

import pytest
from datetime import datetime
from models.requirement import (
    Requirement,
    RequirementCategory,
    RequirementPriority,
    get_category_display_names,
    get_priority_display_names,
)


class TestRequirementModel:
    """Test Requirement data model."""
    
    def test_create_requirement_with_defaults(self):
        """Test creating a requirement with default values."""
        req = Requirement(
            rfp_id="test-rfp-1",
            description="System must support 99.9% uptime"
        )
        
        assert req.rfp_id == "test-rfp-1"
        assert req.description == "System must support 99.9% uptime"
        assert req.category == RequirementCategory.FUNCTIONAL
        assert req.priority == RequirementPriority.MEDIUM
        assert req.confidence == 0.0
        assert req.page_number is None
        assert req.verified is False
        assert req.notes == ""
        assert isinstance(req.id, str)
        assert len(req.id) > 0
    
    def test_create_requirement_with_all_fields(self):
        """Test creating a requirement with all fields specified."""
        req = Requirement(
            rfp_id="test-rfp-1",
            description="Must be HIPAA compliant",
            category=RequirementCategory.COMPLIANCE,
            priority=RequirementPriority.CRITICAL,
            confidence=0.95,
            page_number=5,
            verified=True,
            notes="Verified with client"
        )
        
        assert req.category == RequirementCategory.COMPLIANCE
        assert req.priority == RequirementPriority.CRITICAL
        assert req.confidence == 0.95
        assert req.page_number == 5
        assert req.verified is True
        assert req.notes == "Verified with client"
    
    def test_confidence_validation_min(self):
        """Test confidence cannot be less than 0.0."""
        with pytest.raises(ValueError, match="Confidence must be between 0.0 and 1.0"):
            Requirement(
                rfp_id="test",
                description="Test",
                confidence=-0.1
            )
    
    def test_confidence_validation_max(self):
        """Test confidence cannot be greater than 1.0."""
        with pytest.raises(ValueError, match="Confidence must be between 0.0 and 1.0"):
            Requirement(
                rfp_id="test",
                description="Test",
                confidence=1.1
            )
    
    def test_page_number_validation(self):
        """Test page number must be positive."""
        with pytest.raises(ValueError, match="Page number must be >= 1"):
            Requirement(
                rfp_id="test",
                description="Test",
                page_number=0
            )
    
    def test_category_from_string(self):
        """Test category can be created from string."""
        req = Requirement(
            rfp_id="test",
            description="Test",
            category="technical"
        )
        assert req.category == RequirementCategory.TECHNICAL
    
    def test_priority_from_string(self):
        """Test priority can be created from string."""
        req = Requirement(
            rfp_id="test",
            description="Test",
            priority="high"
        )
        assert req.priority == RequirementPriority.HIGH
    
    def test_to_dict(self):
        """Test serialization to dictionary."""
        req = Requirement(
            rfp_id="test-rfp-1",
            description="Test requirement",
            category=RequirementCategory.TECHNICAL,
            priority=RequirementPriority.HIGH,
            confidence=0.85,
            page_number=3
        )
        
        data = req.to_dict()
        
        assert data["rfp_id"] == "test-rfp-1"
        assert data["description"] == "Test requirement"
        assert data["category"] == "technical"
        assert data["priority"] == "high"
        assert data["confidence"] == 0.85
        assert data["page_number"] == 3
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_from_dict(self):
        """Test deserialization from dictionary."""
        data = {
            "id": "test-id-123",
            "rfp_id": "test-rfp-1",
            "description": "Test requirement",
            "category": "budget",
            "priority": "critical",
            "confidence": 0.90,
            "page_number": 7,
            "verified": True,
            "notes": "Important",
            "created_at": "2025-11-10T12:00:00",
            "updated_at": "2025-11-10T12:00:00"
        }
        
        req = Requirement.from_dict(data)
        
        assert req.id == "test-id-123"
        assert req.rfp_id == "test-rfp-1"
        assert req.description == "Test requirement"
        assert req.category == RequirementCategory.BUDGET
        assert req.priority == RequirementPriority.CRITICAL
        assert req.confidence == 0.90
        assert req.page_number == 7
        assert req.verified is True
    
    def test_update_method(self):
        """Test updating requirement fields."""
        req = Requirement(
            rfp_id="test",
            description="Original",
            verified=False
        )
        
        original_updated_at = req.updated_at
        
        req.update(
            description="Updated description",
            verified=True,
            notes="Added notes"
        )
        
        assert req.description == "Updated description"
        assert req.verified is True
        assert req.notes == "Added notes"
        assert req.updated_at > original_updated_at
    
    def test_get_confidence_label_very_high(self):
        """Test confidence label for very high confidence."""
        req = Requirement(rfp_id="test", description="Test", confidence=0.95)
        assert req.get_confidence_label() == "Very High"
    
    def test_get_confidence_label_high(self):
        """Test confidence label for high confidence."""
        req = Requirement(rfp_id="test", description="Test", confidence=0.80)
        assert req.get_confidence_label() == "High"
    
    def test_get_confidence_label_medium(self):
        """Test confidence label for medium confidence."""
        req = Requirement(rfp_id="test", description="Test", confidence=0.60)
        assert req.get_confidence_label() == "Medium"
    
    def test_get_confidence_label_low(self):
        """Test confidence label for low confidence."""
        req = Requirement(rfp_id="test", description="Test", confidence=0.30)
        assert req.get_confidence_label() == "Low"
    
    def test_get_priority_color(self):
        """Test priority colors for UI."""
        req_critical = Requirement(rfp_id="test", description="Test", priority=RequirementPriority.CRITICAL)
        req_high = Requirement(rfp_id="test", description="Test", priority=RequirementPriority.HIGH)
        req_medium = Requirement(rfp_id="test", description="Test", priority=RequirementPriority.MEDIUM)
        req_low = Requirement(rfp_id="test", description="Test", priority=RequirementPriority.LOW)
        
        assert req_critical.get_priority_color() == "#FF4444"
        assert req_high.get_priority_color() == "#FF8800"
        assert req_medium.get_priority_color() == "#FFBB00"
        assert req_low.get_priority_color() == "#4CAF50"
    
    def test_get_category_icon(self):
        """Test category icons for UI."""
        categories_icons = {
            RequirementCategory.TECHNICAL: "⚙️",
            RequirementCategory.FUNCTIONAL: "🎯",
            RequirementCategory.TIMELINE: "📅",
            RequirementCategory.BUDGET: "💰",
            RequirementCategory.COMPLIANCE: "✅",
        }
        
        for category, expected_icon in categories_icons.items():
            req = Requirement(rfp_id="test", description="Test", category=category)
            assert req.get_category_icon() == expected_icon


class TestRequirementEnums:
    """Test requirement enums and helper functions."""
    
    def test_requirement_category_values(self):
        """Test all RequirementCategory values."""
        assert RequirementCategory.TECHNICAL.value == "technical"
        assert RequirementCategory.FUNCTIONAL.value == "functional"
        assert RequirementCategory.TIMELINE.value == "timeline"
        assert RequirementCategory.BUDGET.value == "budget"
        assert RequirementCategory.COMPLIANCE.value == "compliance"
    
    def test_requirement_priority_values(self):
        """Test all RequirementPriority values."""
        assert RequirementPriority.CRITICAL.value == "critical"
        assert RequirementPriority.HIGH.value == "high"
        assert RequirementPriority.MEDIUM.value == "medium"
        assert RequirementPriority.LOW.value == "low"
    
    def test_get_category_display_names(self):
        """Test category display names helper."""
        names = get_category_display_names()
        
        assert names["technical"] == "Technical"
        assert names["functional"] == "Functional"
        assert names["timeline"] == "Timeline"
        assert names["budget"] == "Budget"
        assert names["compliance"] == "Compliance"
        assert len(names) == 5
    
    def test_get_priority_display_names(self):
        """Test priority display names helper."""
        names = get_priority_display_names()
        
        assert names["critical"] == "Critical"
        assert names["high"] == "High"
        assert names["medium"] == "Medium"
        assert names["low"] == "Low"
        assert len(names) == 4

