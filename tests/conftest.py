"""Pytest configuration and fixtures."""

import pytest
import sys
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models import RFP, Requirement, RequirementCategory, RequirementPriority


@pytest.fixture
def sample_rfp() -> RFP:
    """Provide sample RFP for testing."""
    return RFP(
        id="rfp-test-001",
        file_name="test_rfp.pdf",
        file_size=1024000,
        uploaded_at=datetime(2025, 11, 1)
    )


@pytest.fixture
def sample_rfp_with_text() -> RFP:
    """Provide sample RFP with extracted text for testing."""
    rfp = RFP(
        id="rfp-test-002",
        file_name="sample_with_text.pdf",
        file_size=2048000,
        uploaded_at=datetime(2025, 11, 1)
    )
    rfp.extracted_text = """
    REQUIREMENTS FOR PROPOSAL
    
    Technical Requirements:
    - System must support 99.9% uptime SLA
    - AWS cloud infrastructure required
    
    Timeline:
    - Project completion within 90 days
    
    Budget:
    - Total cost not to exceed $500,000 USD
    """
    rfp.extracted_text_by_page = {
        1: "Technical Requirements: System must support 99.9% uptime SLA",
        2: "Budget: Total cost not to exceed $500,000 USD"
    }
    return rfp


@pytest.fixture
def sample_requirement() -> Requirement:
    """Provide sample requirement for testing."""
    return Requirement(
        id="req-test-001",
        rfp_id="rfp-test-001",
        description="System must support 99.9% uptime SLA",
        category=RequirementCategory.TECHNICAL,
        priority=RequirementPriority.CRITICAL,
        confidence=0.92
    )


@pytest.fixture
def test_pdf_path() -> Path:
    """Provide path to test PDF."""
    return Path(__file__).parent / "fixtures" / "sample_rfp.pdf"


@pytest.fixture
def mock_llm_client():
    """Provide mock LLM client for testing."""
    from unittest.mock import Mock
    
    mock_client = Mock()
    mock_client.generate.return_value = "Mock LLM response"
    mock_client.extract_json.return_value = [
        {
            "description": "Mock requirement",
            "category": "technical",
            "priority": "high",
            "confidence": 0.85,
            "page_number": 1
        }
    ]
    mock_client.test_connection.return_value = True
    
    return mock_client


@pytest.fixture
def sample_requirements_list():
    """Provide list of sample requirements for testing."""
    return [
        Requirement(
            rfp_id="rfp-test-001",
            description="System must support 99.9% uptime SLA",
            category=RequirementCategory.TECHNICAL,
            priority=RequirementPriority.CRITICAL,
            confidence=0.95,
            page_number=1
        ),
        Requirement(
            rfp_id="rfp-test-001",
            description="Project completion within 90 days",
            category=RequirementCategory.TIMELINE,
            priority=RequirementPriority.HIGH,
            confidence=0.90,
            page_number=2
        ),
        Requirement(
            rfp_id="rfp-test-001",
            description="Total budget not to exceed $500K",
            category=RequirementCategory.BUDGET,
            priority=RequirementPriority.CRITICAL,
            confidence=0.92,
            page_number=3
        ),
    ]

