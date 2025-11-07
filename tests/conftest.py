"""Pytest configuration and fixtures."""

import pytest
from pathlib import Path
from datetime import datetime
from src.models import RFP, Requirement, Service, RiskClause, Draft


@pytest.fixture
def sample_rfp() -> RFP:
    """Provide sample RFP for testing."""
    return RFP(
        id="rfp-test-001",
        title="Test RFP - Cloud Migration",
        file_name="test_rfp.pdf",
        file_size=1024000,
        file_path="data/uploads/test_rfp.pdf",
        total_pages=25,
        client_name="Test Corp",
        deadline=datetime(2025, 12, 31),
        uploaded_by="test@company.com"
    )


@pytest.fixture
def sample_requirement() -> Requirement:
    """Provide sample requirement for testing."""
    from src.models.requirement import RequirementCategory, RequirementPriority
    
    return Requirement(
        id="req-test-001",
        rfp_id="rfp-test-001",
        description="System must support 99.9% uptime SLA",
        category=RequirementCategory.TECHNICAL,
        priority=RequirementPriority.CRITICAL,
        confidence_score=0.92
    )


@pytest.fixture
def sample_service() -> Service:
    """Provide sample service for testing."""
    from src.models.service import ServiceCategory, PricingModel
    
    return Service(
        id="svc-test-001",
        name="Cloud Infrastructure Migration",
        category=ServiceCategory.CLOUD,
        tags=["cloud", "migration", "aws", "high-availability"],
        description="Comprehensive cloud migration service",
        capabilities=[
            "Multi-cloud migration",
            "High availability architecture",
            "24/7 monitoring"
        ],
        pricing_model=PricingModel.CUSTOM,
        past_projects=50,
        success_rate=0.94
    )


@pytest.fixture
def sample_risk() -> RiskClause:
    """Provide sample risk clause for testing."""
    from src.models.risk import RiskType, RiskSeverity
    
    return RiskClause(
        id="risk-test-001",
        rfp_id="rfp-test-001",
        risk_type=RiskType.FINANCIAL,
        severity=RiskSeverity.HIGH,
        clause_text="Unlimited revisions at no additional cost",
        risk_description="Unbounded cost liability",
        recommendation="Propose maximum 3 revision rounds",
        confidence_score=0.88
    )


@pytest.fixture
def sample_draft() -> Draft:
    """Provide sample draft for testing."""
    from src.models.draft import DraftStatus, GenerationMethod
    
    return Draft(
        id="draft-test-001",
        rfp_id="rfp-test-001",
        title="Test Proposal",
        content="# Proposal\n\nTest content...",
        word_count=500,
        status=DraftStatus.GENERATED,
        generated_by=GenerationMethod.AI
    )


@pytest.fixture
def test_pdf_path() -> Path:
    """Provide path to test PDF."""
    return Path(__file__).parent / "fixtures" / "sample_rfp.pdf"


@pytest.fixture
def mock_llm():
    """Provide mock LLM for testing."""
    class MockLLM:
        def generate(self, prompt: str) -> str:
            return "Mock LLM response"
        
        def embed(self, text: str) -> list:
            return [0.1] * 1536
    
    return MockLLM()

