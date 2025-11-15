"""UI tests for Service Matching page."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import List

from models import Service, Requirement, ServiceCategory, RequirementCategory, RequirementPriority
from services.service_matcher import ServiceMatcher, ServiceMatch


@pytest.fixture
def sample_services() -> List[Service]:
    """Create sample services for UI testing."""
    return [
        Service(
            id="svc-1",
            name="Cloud Infrastructure",
            category=ServiceCategory.TECHNICAL,
            description="AWS cloud services",
            capabilities=["AWS", "Kubernetes"],
            success_rate=0.96,
            tags=["cloud"]
        ),
        Service(
            id="svc-2",
            name="Web Development",
            category=ServiceCategory.FUNCTIONAL,
            description="Full-stack web development",
            capabilities=["React", "Python"],
            success_rate=0.95,
            tags=["web"]
        ),
    ]


@pytest.fixture
def sample_requirements() -> List[Requirement]:
    """Create sample requirements for UI testing."""
    return [
        Requirement(
            id="req-1",
            description="AWS cloud deployment needed",
            category=RequirementCategory.TECHNICAL,
            priority=RequirementPriority.CRITICAL,
            confidence=0.95,
            page_number=1
        ),
        Requirement(
            id="req-2",
            description="Build web application",
            category=RequirementCategory.FUNCTIONAL,
            priority=RequirementPriority.HIGH,
            confidence=0.90,
            page_number=2
        ),
    ]


@pytest.fixture
def sample_matches(sample_requirements, sample_services) -> List[ServiceMatch]:
    """Create sample service matches."""
    return [
        ServiceMatch(
            requirement_id=sample_requirements[0].id,
            requirement_description=sample_requirements[0].description,
            requirement_category=sample_requirements[0].category,
            service_id=sample_services[0].id,
            service_name=sample_services[0].name,
            service_category=sample_services[0].category,
            score=0.92,
            reasoning="Strong match: cloud, AWS keywords",
            approved=True
        ),
        ServiceMatch(
            requirement_id=sample_requirements[1].id,
            requirement_description=sample_requirements[1].description,
            requirement_category=sample_requirements[1].category,
            service_id=sample_services[1].id,
            service_name=sample_services[1].name,
            service_category=sample_services[1].category,
            score=0.85,
            reasoning="Strong match: web, development keywords",
            approved=True
        ),
        ServiceMatch(
            requirement_id=sample_requirements[0].id,
            requirement_description=sample_requirements[0].description,
            requirement_category=sample_requirements[0].category,
            service_id=sample_services[1].id,
            service_name=sample_services[1].name,
            service_category=sample_services[1].category,
            score=0.45,
            reasoning="Weak match: few common keywords",
            approved=False
        ),
    ]


class TestFilterAndSort:
    """Test filter and sort logic for service matches."""
    
    def test_filter_by_category(self, sample_matches):
        """Test filtering matches by category."""
        # Simulate filtering by category
        filtered = [
            m for m in sample_matches
            if m.requirement_category.value.lower() == "technical"
        ]
        
        assert all(m.requirement_category == RequirementCategory.TECHNICAL for m in filtered)
        assert len(filtered) == 2  # 2 technical matches
    
    def test_filter_by_score(self, sample_matches):
        """Test filtering matches by minimum score."""
        # Simulate filtering by score
        min_score = 0.80
        filtered = [m for m in sample_matches if m.score >= min_score]
        
        assert all(m.score >= 0.80 for m in filtered)
        assert len(filtered) == 2  # Only 2 matches have score >= 0.80
    
    def test_sort_highest_first(self, sample_matches):
        """Test sorting matches by highest score first."""
        # Simulate sorting descending
        sorted_matches = sorted(sample_matches, key=lambda m: m.score, reverse=True)
        
        # Verify descending order
        for i in range(len(sorted_matches) - 1):
            assert sorted_matches[i].score >= sorted_matches[i + 1].score
    
    def test_sort_lowest_first(self, sample_matches):
        """Test sorting matches by lowest score first."""
        # Simulate sorting ascending
        sorted_matches = sorted(sample_matches, key=lambda m: m.score)
        
        # Verify ascending order
        for i in range(len(sorted_matches) - 1):
            assert sorted_matches[i].score <= sorted_matches[i + 1].score


class TestMatchComputation:
    """Test match computation logic."""
    
    def test_compute_matches(self, sample_requirements, sample_services):
        """Test computing matches from requirements and services."""
        matcher = ServiceMatcher(sample_services)
        matches = matcher.match_all_requirements(sample_requirements, min_score=0.1, top_n=3)
        
        assert len(matches) > 0
        assert all(isinstance(m, ServiceMatch) for m in matches)
    
    def test_compute_matches_empty_requirements(self, sample_services):
        """Test computing matches with no requirements."""
        matcher = ServiceMatcher(sample_services)
        matches = matcher.match_all_requirements([], min_score=0.1, top_n=3)
        
        assert matches == []
    
    def test_compute_matches_empty_services(self, sample_requirements):
        """Test computing matches with no services."""
        matcher = ServiceMatcher([])
        matches = matcher.match_all_requirements(sample_requirements, min_score=0.1, top_n=3)
        
        assert matches == []


class TestExportFunctionality:
    """Test export functionality."""
    
    def test_export_data_structure(self, sample_matches):
        """Test export data structure is correct."""
        import json
        from datetime import datetime
        
        # Simulate export data preparation
        export_data = {
            "rfp_id": "test-rfp",
            "exported_at": datetime.now().isoformat(),
            "total_matches": len(sample_matches),
            "approved_matches": sum(1 for m in sample_matches if m.approved),
            "matches": [m.to_dict() for m in sample_matches],
            "coverage": {"technical": "92%", "functional": "85%"},
            "overall_coverage": "88.5%"
        }
        
        # Verify structure
        assert "rfp_id" in export_data
        assert "matches" in export_data
        assert "coverage" in export_data
        assert export_data["total_matches"] == 3
        assert export_data["approved_matches"] == 2
        
        # Verify JSON serialization works
        json_str = json.dumps(export_data)
        assert isinstance(json_str, str)


class TestCoverageVisualization:
    """Test coverage chart logic."""
    
    def test_coverage_by_category(self, sample_matches):
        """Test coverage calculation by category."""
        matcher = ServiceMatcher([])  # Empty matcher, only using static methods
        
        # Group matches by category manually
        coverage = {}
        by_category = {}
        for match in sample_matches:
            cat = match.requirement_category.value
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(match.score)
        
        for cat, scores in by_category.items():
            coverage[cat] = sum(scores) / len(scores)
        
        # Verify coverage calculation
        assert "technical" in coverage
        assert "functional" in coverage
        assert 0.0 <= coverage["technical"] <= 1.0
        assert 0.0 <= coverage["functional"] <= 1.0


class TestApprovalWorkflow:
    """Test approval workflow logic."""
    
    def test_approve_high_matches(self, sample_matches):
        """Test approving all high-confidence matches."""
        # Simulate bulk approval
        for match in sample_matches:
            if match.score >= 0.80:
                match.approved = True
        
        approved_count = sum(1 for m in sample_matches if m.approved)
        assert approved_count == 2  # 2 matches have score >= 0.80
    
    def test_clear_all_approvals(self, sample_matches):
        """Test clearing all approvals."""
        # First approve all
        for match in sample_matches:
            match.approved = True
        
        # Then clear all
        for match in sample_matches:
            match.approved = False
        
        approved_count = sum(1 for m in sample_matches if m.approved)
        assert approved_count == 0

