"""Unit tests for ServiceMatcher engine."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import List

from models import Service, Requirement, ServiceCategory, RequirementCategory, RequirementPriority
from services.service_matcher import ServiceMatcher, ServiceMatch


@pytest.fixture
def sample_services() -> List[Service]:
    """Create sample services for testing."""
    return [
        Service(
            id="cloud-infra",
            name="Cloud Infrastructure",
            category=ServiceCategory.TECHNICAL,
            description="AWS cloud deployment and infrastructure management with Kubernetes",
            capabilities=["AWS", "Kubernetes", "Docker", "CI/CD"],
            success_rate=0.96,
            tags=["cloud", "devops", "aws"]
        ),
        Service(
            id="custom-dev",
            name="Custom Development",
            category=ServiceCategory.FUNCTIONAL,
            description="Full-stack web development using React and Python Django",
            capabilities=["React", "Python", "Django", "REST API"],
            success_rate=0.95,
            tags=["development", "web", "fullstack"]
        ),
        Service(
            id="qa-testing",
            name="QA Testing",
            category=ServiceCategory.COMPLIANCE,
            description="Automated testing with Selenium and manual QA processes",
            capabilities=["Selenium", "Automated Testing", "Manual Testing"],
            success_rate=0.94,
            tags=["qa", "testing", "automation"]
        ),
    ]


@pytest.fixture
def sample_requirements() -> List[Requirement]:
    """Create sample requirements for testing."""
    return [
        Requirement(
            id="req-001",
            description="Deploy application on AWS cloud infrastructure with auto-scaling",
            category=RequirementCategory.TECHNICAL,
            priority=RequirementPriority.CRITICAL,
            confidence=0.95,
            page_number=1
        ),
        Requirement(
            id="req-002",
            description="Develop custom web application using modern JavaScript framework",
            category=RequirementCategory.FUNCTIONAL,
            priority=RequirementPriority.HIGH,
            confidence=0.90,
            page_number=2
        ),
        Requirement(
            id="req-003",
            description="Implement comprehensive automated testing strategy",
            category=RequirementCategory.COMPLIANCE,
            priority=RequirementPriority.MEDIUM,
            confidence=0.85,
            page_number=3
        ),
    ]


class TestServiceMatch:
    """Test ServiceMatch model."""
    
    def test_service_match_creation(self):
        """Test creating a ServiceMatch object."""
        match = ServiceMatch(
            requirement_id="req-001",
            requirement_description="Test requirement",
            requirement_category=RequirementCategory.TECHNICAL,
            service_id="service-001",
            service_name="Test Service",
            service_category=ServiceCategory.TECHNICAL,
            score=0.85,
            reasoning="Strong match based on keywords",
            approved=True
        )
        
        assert match.requirement_id == "req-001"
        assert match.service_id == "service-001"
        assert match.score == 0.85
        assert match.approved is True
    
    def test_service_match_to_dict(self):
        """Test converting ServiceMatch to dictionary."""
        match = ServiceMatch(
            requirement_id="req-001",
            requirement_description="Test requirement",
            requirement_category=RequirementCategory.TECHNICAL,
            service_id="service-001",
            service_name="Test Service",
            service_category=ServiceCategory.TECHNICAL,
            score=0.85
        )
        
        data = match.to_dict()
        
        assert isinstance(data, dict)
        assert data["requirement_id"] == "req-001"
        assert data["service_id"] == "service-001"
        assert data["score"] == 0.85
        assert data["requirement_category"] == "technical"
        assert data["service_category"] == "technical"
    
    def test_service_match_from_dict(self):
        """Test creating ServiceMatch from dictionary."""
        data = {
            "requirement_id": "req-001",
            "requirement_description": "Test requirement",
            "requirement_category": "technical",
            "service_id": "service-001",
            "service_name": "Test Service",
            "service_category": "technical",
            "score": 0.85,
            "reasoning": "Test reasoning",
            "approved": True
        }
        
        match = ServiceMatch.from_dict(data)
        
        assert match.requirement_id == "req-001"
        assert match.service_id == "service-001"
        assert match.score == 0.85
        assert match.approved is True


class TestServiceMatcher:
    """Test ServiceMatcher engine."""
    
    def test_matcher_initialization(self, sample_services):
        """Test initializing ServiceMatcher."""
        matcher = ServiceMatcher(sample_services)
        
        assert matcher.services == sample_services
        assert matcher.vectorizer is not None
        assert matcher.service_vectors is not None
    
    def test_matcher_empty_services(self):
        """Test matcher with empty service list."""
        matcher = ServiceMatcher([])
        
        assert matcher.services == []
        assert matcher.vectorizer is None
        assert matcher.service_vectors is None
    
    def test_match_requirement_single(self, sample_services, sample_requirements):
        """Test matching a single requirement."""
        matcher = ServiceMatcher(sample_services)
        req = sample_requirements[0]  # AWS cloud requirement
        
        matches = matcher.match_requirement(req, top_n=3, min_score=0.0)
        
        assert len(matches) > 0
        assert all(isinstance(m, ServiceMatch) for m in matches)
        assert matches[0].requirement_id == req.id
        # Should match cloud service highest
        assert "cloud" in matches[0].service_name.lower() or "infra" in matches[0].service_name.lower()
    
    def test_match_requirement_with_score_threshold(self, sample_services, sample_requirements):
        """Test matching with minimum score threshold."""
        matcher = ServiceMatcher(sample_services)
        req = sample_requirements[0]
        
        matches_low = matcher.match_requirement(req, top_n=3, min_score=0.1)
        matches_high = matcher.match_requirement(req, top_n=3, min_score=0.9)
        
        # Low threshold should give more results
        assert len(matches_low) >= len(matches_high)
        # All high-threshold matches should have score >= 0.9
        assert all(m.score >= 0.9 for m in matches_high)
    
    def test_match_all_requirements(self, sample_services, sample_requirements):
        """Test matching all requirements in batch."""
        matcher = ServiceMatcher(sample_services)
        
        all_matches = matcher.match_all_requirements(sample_requirements, top_n=2, min_score=0.0)
        
        # Should have matches for each requirement (2 per req)
        assert len(all_matches) <= len(sample_requirements) * 2
        assert all(isinstance(m, ServiceMatch) for m in all_matches)
    
    def test_match_auto_approval(self, sample_services, sample_requirements):
        """Test automatic approval of high-confidence matches (>80%)."""
        matcher = ServiceMatcher(sample_services)
        req = sample_requirements[0]  # Should match cloud service well
        
        matches = matcher.match_requirement(req, top_n=3, min_score=0.0)
        
        # Check if any matches with score >= 0.80 are auto-approved
        high_matches = [m for m in matches if m.score >= 0.80]
        if high_matches:
            assert all(m.approved for m in high_matches)
    
    def test_calculate_coverage_by_category(self, sample_services, sample_requirements):
        """Test calculating coverage by requirement category."""
        matcher = ServiceMatcher(sample_services)
        matches = matcher.match_all_requirements(sample_requirements, top_n=2, min_score=0.0)
        
        coverage = matcher.calculate_coverage_by_category(matches)
        
        assert isinstance(coverage, dict)
        # Should have coverage for at least one category
        assert len(coverage) > 0
        # All scores should be between 0.0 and 1.0
        assert all(0.0 <= score <= 1.0 for score in coverage.values())
    
    def test_get_overall_coverage(self, sample_services, sample_requirements):
        """Test getting overall average coverage."""
        matcher = ServiceMatcher(sample_services)
        matches = matcher.match_all_requirements(sample_requirements, top_n=2, min_score=0.0)
        
        overall = matcher.get_overall_coverage(matches)
        
        assert isinstance(overall, float)
        assert 0.0 <= overall <= 1.0
    
    def test_count_approved_matches(self, sample_services, sample_requirements):
        """Test counting approved vs. total matches."""
        matcher = ServiceMatcher(sample_services)
        matches = matcher.match_all_requirements(sample_requirements, top_n=2, min_score=0.0)
        
        approved, total = matcher.count_approved_matches(matches)
        
        assert isinstance(approved, int)
        assert isinstance(total, int)
        assert 0 <= approved <= total
        assert total == len(matches)
    
    def test_color_for_score(self):
        """Test color indicator for different score ranges."""
        # High score (>= 0.80) should be green
        assert ServiceMatcher.color_for_score(0.90) == "🟢"
        assert ServiceMatcher.color_for_score(0.80) == "🟢"
        
        # Moderate score (0.50-0.79) should be yellow
        assert ServiceMatcher.color_for_score(0.70) == "🟡"
        assert ServiceMatcher.color_for_score(0.50) == "🟡"
        
        # Low score (< 0.50) should be red
        assert ServiceMatcher.color_for_score(0.40) == "🔴"
        assert ServiceMatcher.color_for_score(0.10) == "🔴"
    
    def test_generate_reasoning(self, sample_services, sample_requirements):
        """Test reasoning generation for matches."""
        matcher = ServiceMatcher(sample_services)
        req = sample_requirements[0]
        service = sample_services[0]
        
        reasoning = matcher._generate_reasoning(req, service, 0.85)
        
        assert isinstance(reasoning, str)
        assert len(reasoning) > 0
        # Should mention the score
        assert "85%" in reasoning or "Strong match" in reasoning
    
    def test_empty_matches_coverage(self, sample_services):
        """Test coverage calculation with empty matches."""
        matcher = ServiceMatcher(sample_services)
        
        coverage = matcher.calculate_coverage_by_category([])
        overall = matcher.get_overall_coverage([])
        
        assert coverage == {}
        assert overall == 0.0
    
    def test_match_with_no_services(self, sample_requirements):
        """Test matching when no services are available."""
        matcher = ServiceMatcher([])
        req = sample_requirements[0]
        
        matches = matcher.match_requirement(req, top_n=3)
        
        assert matches == []

