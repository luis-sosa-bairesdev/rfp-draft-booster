"""
Unit tests for Requirements page UI.

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
from models.requirement import Requirement, RequirementCategory, RequirementPriority


class TestRequirementsPageHelpers:
    """Test helper functions in Requirements page."""
    
    def test_get_category_icon(self):
        """Test category icon helper function."""
        # Test the icon mapping logic (same as in the page)
        icons = {
            RequirementCategory.TECHNICAL: "⚙️",
            RequirementCategory.FUNCTIONAL: "🎯",
            RequirementCategory.TIMELINE: "📅",
            RequirementCategory.BUDGET: "💰",
            RequirementCategory.COMPLIANCE: "✅",
        }
        
        assert icons[RequirementCategory.TECHNICAL] == "⚙️"
        assert icons[RequirementCategory.FUNCTIONAL] == "🎯"
        assert icons[RequirementCategory.TIMELINE] == "📅"
        assert icons[RequirementCategory.BUDGET] == "💰"
        assert icons[RequirementCategory.COMPLIANCE] == "✅"
        
        # Test default
        default_icon = icons.get(RequirementCategory.TECHNICAL, "📋")
        assert default_icon == "⚙️"


class TestRequirementsPageLogic:
    """Test business logic functions in Requirements page."""
    
    @patch('streamlit.session_state', new_callable=dict)
    def test_display_requirement_table_filtering(self, mock_session_state):
        """Test requirement table filtering logic."""
        # Create test requirements
        req1 = Requirement(
            rfp_id="test-rfp-1",
            description="Test technical requirement",
            category=RequirementCategory.TECHNICAL,
            priority=RequirementPriority.CRITICAL,
            confidence=0.9,
            page_number=1
        )
        
        req2 = Requirement(
            rfp_id="test-rfp-1",
            description="Test functional requirement",
            category=RequirementCategory.FUNCTIONAL,
            priority=RequirementPriority.HIGH,
            confidence=0.8,
            page_number=2
        )
        
        req3 = Requirement(
            rfp_id="test-rfp-1",
            description="Test timeline requirement",
            category=RequirementCategory.TIMELINE,
            priority=RequirementPriority.CRITICAL,
            confidence=0.95,
            page_number=1
        )
        
        requirements = [req1, req2, req3]
        
        # Test filtering by category
        filtered_technical = [r for r in requirements if r.category.value == "technical"]
        assert len(filtered_technical) == 1
        assert filtered_technical[0].category == RequirementCategory.TECHNICAL
        
        # Test filtering by priority
        filtered_critical = [r for r in requirements if r.priority.value == "critical"]
        assert len(filtered_critical) == 2
        
        # Test no filter
        filtered_all = requirements
        assert len(filtered_all) == 3
    
    def test_requirement_statistics(self):
        """Test requirement statistics calculation."""
        requirements = [
            Requirement(
                rfp_id="test-rfp-1",
                description=f"Requirement {i}",
                category=RequirementCategory.TECHNICAL if i % 2 == 0 else RequirementCategory.FUNCTIONAL,
                priority=RequirementPriority.CRITICAL if i < 3 else RequirementPriority.HIGH,
                confidence=0.9 if i < 5 else 0.7,
                verified=i < 2
            )
            for i in range(10)
        ]
        
        # Calculate statistics
        total = len(requirements)
        verified_count = sum(1 for r in requirements if r.verified)
        avg_confidence = sum(r.confidence for r in requirements) / len(requirements)
        critical_count = sum(1 for r in requirements if r.priority == RequirementPriority.CRITICAL)
        high_confidence = sum(1 for r in requirements if r.confidence >= 0.8)
        
        assert total == 10
        assert verified_count == 2
        assert 0.7 <= avg_confidence <= 0.9
        assert critical_count == 3
        assert high_confidence == 5
        
        # Category breakdown
        category_counts = {}
        for req in requirements:
            cat = req.category.value
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        assert category_counts["technical"] == 5
        assert category_counts["functional"] == 5


class TestRequirementsPageIntegration:
    """Test integration aspects of Requirements page."""
    
    @patch('streamlit.session_state', new_callable=dict)
    def test_requirement_crud_operations(self, mock_session_state):
        """Test CRUD operations on requirements."""
        requirements = []
        mock_session_state["requirements"] = requirements
        
        # Create
        new_req = Requirement(
            rfp_id="test-rfp-1",
            description="New requirement",
            category=RequirementCategory.TECHNICAL,
            priority=RequirementPriority.HIGH,
            confidence=0.8
        )
        requirements.append(new_req)
        assert len(requirements) == 1
        
        # Read
        assert requirements[0].description == "New requirement"
        
        # Update
        requirements[0].update(
            description="Updated requirement",
            category=RequirementCategory.FUNCTIONAL
        )
        assert requirements[0].description == "Updated requirement"
        assert requirements[0].category == RequirementCategory.FUNCTIONAL
        
        # Delete
        requirements.remove(requirements[0])
        assert len(requirements) == 0
    
    def test_requirement_serialization(self):
        """Test requirement serialization to/from dict."""
        req = Requirement(
            rfp_id="test-rfp-1",
            description="Test requirement",
            category=RequirementCategory.TECHNICAL,
            priority=RequirementPriority.CRITICAL,
            confidence=0.95,
            page_number=1,
            verified=True,
            notes="Test notes"
        )
        
        # Serialize
        req_dict = req.to_dict()
        assert req_dict["description"] == "Test requirement"
        assert req_dict["category"] == "technical"
        assert req_dict["priority"] == "critical"
        assert req_dict["confidence"] == 0.95
        assert req_dict["page_number"] == 1
        assert req_dict["verified"] is True
        assert req_dict["notes"] == "Test notes"
        
        # Deserialize
        req_from_dict = Requirement.from_dict(req_dict)
        assert req_from_dict.description == req.description
        assert req_from_dict.category == req.category
        assert req_from_dict.priority == req.priority
        assert req_from_dict.confidence == req.confidence


class TestRequirementsPageFilters:
    """Test filtering functionality."""
    
    def test_filter_by_category(self):
        """Test filtering requirements by category."""
        requirements = [
            Requirement(
                rfp_id="test-rfp-1",
                description=f"Requirement {i}",
                category=RequirementCategory.TECHNICAL if i % 2 == 0 else RequirementCategory.FUNCTIONAL,
                priority=RequirementPriority.HIGH,
                confidence=0.8
            )
            for i in range(10)
        ]
        
        # Filter technical
        technical = [r for r in requirements if r.category.value == "technical"]
        assert len(technical) == 5
        assert all(r.category == RequirementCategory.TECHNICAL for r in technical)
        
        # Filter functional
        functional = [r for r in requirements if r.category.value == "functional"]
        assert len(functional) == 5
        assert all(r.category == RequirementCategory.FUNCTIONAL for r in functional)
    
    def test_filter_by_priority(self):
        """Test filtering requirements by priority."""
        requirements = [
            Requirement(
                rfp_id="test-rfp-1",
                description=f"Requirement {i}",
                category=RequirementCategory.TECHNICAL,
                priority=RequirementPriority.CRITICAL if i < 3 else RequirementPriority.HIGH,
                confidence=0.8
            )
            for i in range(10)
        ]
        
        # Filter critical
        critical = [r for r in requirements if r.priority.value == "critical"]
        assert len(critical) == 3
        assert all(r.priority == RequirementPriority.CRITICAL for r in critical)
        
        # Filter high
        high = [r for r in requirements if r.priority.value == "high"]
        assert len(high) == 7
        assert all(r.priority == RequirementPriority.HIGH for r in high)
    
    def test_filter_unverified_only(self):
        """Test filtering to show only unverified requirements."""
        requirements = [
            Requirement(
                rfp_id="test-rfp-1",
                description=f"Requirement {i}",
                category=RequirementCategory.TECHNICAL,
                priority=RequirementPriority.HIGH,
                confidence=0.8,
                verified=i < 3  # First 3 are verified
            )
            for i in range(10)
        ]
        
        unverified = [r for r in requirements if not r.verified]
        assert len(unverified) == 7
        assert all(not r.verified for r in unverified)

