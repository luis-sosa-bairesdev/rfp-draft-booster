"""
Unit tests for mock_data module.

Tests mock data generation for requirements, risks, drafts, and RFPs.
"""

import pytest
from datetime import datetime

from src.utils.mock_data import (
    generate_mock_requirements,
    generate_mock_risks,
    generate_mock_draft,
    generate_mock_rfp,
    is_mock_data_enabled,
    MOCK_REQUIREMENTS,
    MOCK_RISKS
)


class TestMockRequirements:
    """Test mock requirement generation."""
    
    def test_generate_all_requirements(self):
        """Test generating all mock requirements."""
        requirements = generate_mock_requirements()
        assert len(requirements) == len(MOCK_REQUIREMENTS)
        assert all("id" in req for req in requirements)
        assert all("description" in req for req in requirements)
        assert all("category" in req for req in requirements)
    
    def test_generate_specific_count(self):
        """Test generating a specific number of requirements."""
        requirements = generate_mock_requirements(count=3)
        assert len(requirements) == 3
    
    def test_generate_more_than_available(self):
        """Test generating more requirements than base templates."""
        count = len(MOCK_REQUIREMENTS) * 2
        requirements = generate_mock_requirements(count=count)
        assert len(requirements) == count
        # Check that IDs are unique
        ids = [req["id"] for req in requirements]
        assert len(set(ids)) == count
    
    def test_generate_with_seed(self):
        """Test that same seed produces same results."""
        req1 = generate_mock_requirements(count=5, seed=42)
        req2 = generate_mock_requirements(count=5, seed=42)
        assert req1 == req2
    
    def test_requirement_structure(self):
        """Test that generated requirements have correct structure."""
        requirements = generate_mock_requirements(count=1)
        req = requirements[0]
        
        assert "id" in req
        assert "description" in req
        assert "category" in req
        assert "priority" in req
        assert "confidence" in req
        assert "page_number" in req
        assert "verified" in req
        assert "source" in req
    
    def test_requirement_values(self):
        """Test that requirement values are valid."""
        requirements = generate_mock_requirements()
        
        for req in requirements:
            assert isinstance(req["description"], str)
            assert len(req["description"]) >= 10
            assert req["category"] in ["Technical", "Functional", "Timeline", "Budget", "Compliance"]
            assert req["priority"] in ["Critical", "High", "Medium", "Low"]
            assert 0.0 <= req["confidence"] <= 1.0
            assert req["page_number"] >= 1


class TestMockRisks:
    """Test mock risk generation."""
    
    def test_generate_all_risks(self):
        """Test generating all mock risks."""
        risks = generate_mock_risks()
        assert len(risks) == len(MOCK_RISKS)
        assert all("id" in risk for risk in risks)
        assert all("clause_text" in risk for risk in risks)
        assert all("category" in risk for risk in risks)
    
    def test_generate_specific_count(self):
        """Test generating a specific number of risks."""
        risks = generate_mock_risks(count=3)
        assert len(risks) == 3
    
    def test_generate_more_than_available(self):
        """Test generating more risks than base templates."""
        count = len(MOCK_RISKS) * 2
        risks = generate_mock_risks(count=count)
        assert len(risks) == count
        # Check that IDs are unique
        ids = [risk["id"] for risk in risks]
        assert len(set(ids)) == count
    
    def test_generate_with_seed(self):
        """Test that same seed produces same results."""
        risks1 = generate_mock_risks(count=3, seed=42)
        risks2 = generate_mock_risks(count=3, seed=42)
        assert risks1 == risks2
    
    def test_risk_structure(self):
        """Test that generated risks have correct structure."""
        risks = generate_mock_risks(count=1)
        risk = risks[0]
        
        assert "id" in risk
        assert "clause_text" in risk
        assert "category" in risk
        assert "severity" in risk
        assert "confidence" in risk
        assert "page_number" in risk
        assert "recommendation" in risk
        assert "alternative_language" in risk
        assert "acknowledged" in risk
    
    def test_risk_values(self):
        """Test that risk values are valid."""
        risks = generate_mock_risks()
        
        for risk in risks:
            assert isinstance(risk["clause_text"], str)
            assert len(risk["clause_text"]) >= 10
            assert risk["category"] in ["Legal", "Financial", "Timeline", "Technical", "Compliance"]
            assert risk["severity"] in ["Critical", "High", "Medium", "Low"]
            assert 0.0 <= risk["confidence"] <= 1.0
            assert risk["page_number"] >= 1


class TestMockDraft:
    """Test mock draft generation."""
    
    def test_generate_draft(self):
        """Test generating a mock draft."""
        draft = generate_mock_draft()
        
        assert "id" in draft
        assert "rfp_id" in draft
        assert "content" in draft
        assert "status" in draft
        assert "generated_by" in draft
        assert "word_count" in draft
        assert "section_count" in draft
        assert "completeness_score" in draft
    
    def test_generate_draft_custom_rfp_id(self):
        """Test generating draft with custom RFP ID."""
        rfp_id = "custom-rfp-123"
        draft = generate_mock_draft(rfp_id=rfp_id)
        
        assert draft["rfp_id"] == rfp_id
        assert draft["id"] == f"draft-{rfp_id}"
    
    def test_draft_content(self):
        """Test that draft content is valid."""
        draft = generate_mock_draft()
        
        assert isinstance(draft["content"], str)
        assert len(draft["content"]) > 100
        assert "Executive Summary" in draft["content"]
        assert "Technical Approach" in draft["content"]
    
    def test_draft_metrics(self):
        """Test that draft metrics are calculated."""
        draft = generate_mock_draft()
        
        assert draft["word_count"] > 0
        assert draft["section_count"] > 0
        assert 0.0 <= draft["completeness_score"] <= 1.0


class TestMockRFP:
    """Test mock RFP generation."""
    
    def test_generate_rfp(self):
        """Test generating a mock RFP."""
        rfp = generate_mock_rfp()
        
        assert "id" in rfp
        assert "file_name" in rfp
        assert "client_name" in rfp
        assert "extracted_text" in rfp
        assert "page_count" in rfp
        assert "deadline" in rfp
        assert "upload_date" in rfp
    
    def test_generate_rfp_custom_values(self):
        """Test generating RFP with custom values."""
        file_name = "custom-rfp.pdf"
        client_name = "Custom Client Inc"
        
        rfp = generate_mock_rfp(file_name=file_name, client_name=client_name)
        
        assert rfp["file_name"] == file_name
        assert rfp["client_name"] == client_name
    
    def test_rfp_dates(self):
        """Test that RFP dates are valid ISO format."""
        rfp = generate_mock_rfp()
        
        # Parse dates to verify they're valid ISO format
        deadline = datetime.fromisoformat(rfp["deadline"])
        upload_date = datetime.fromisoformat(rfp["upload_date"])
        
        # Deadline should be in the future
        assert deadline > datetime.now()
        # Upload date should be now (approximately)
        assert (datetime.now() - upload_date).total_seconds() < 5
    
    def test_rfp_values(self):
        """Test that RFP values are valid."""
        rfp = generate_mock_rfp()
        
        assert rfp["file_name"].endswith(".pdf")
        assert len(rfp["client_name"]) >= 2
        assert rfp["page_count"] > 0
        assert isinstance(rfp["extracted_text"], str)


class TestMockDataEnabled:
    """Test mock data enabled check."""
    
    def test_is_mock_data_enabled_no_streamlit(self):
        """Test when Streamlit is not available."""
        # Should return False when Streamlit not imported properly
        result = is_mock_data_enabled()
        assert result is False

