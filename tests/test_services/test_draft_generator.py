"""
Unit tests for Draft Generator service.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from models import (
    RFP, Requirement, Risk, Draft, DraftSection, DraftStatus, GenerationMethod,
    RequirementCategory, RequirementPriority, RiskCategory, RiskSeverity
)
from services.draft_generator import DraftGenerator
from services.llm_client import LLMClient, LLMProvider


@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client."""
    client = Mock(spec=LLMClient)
    client.provider = LLMProvider.GEMINI
    client.generate = Mock(return_value="""
# Executive Summary

This is the executive summary of our proposal.

## Approach

Our approach involves multiple phases.

## Services & Solutions

We offer comprehensive services.

## Timeline

The project will be completed in phases.

## Pricing

Our pricing is competitive.

## Risk Mitigation

We address all identified risks.
""")
    return client


@pytest.fixture
def sample_rfp():
    """Create a sample RFP for testing."""
    rfp = RFP(
        id="rfp-123",
        file_name="test_rfp.pdf",
        extracted_text="This is a test RFP document."
    )
    rfp.title = "Test RFP"
    return rfp


@pytest.fixture
def sample_requirements():
    """Create sample requirements for testing."""
    return [
        Requirement(
            id="req-1",
            rfp_id="rfp-123",
            description="System must support 99.9% uptime",
            category=RequirementCategory.TECHNICAL,
            priority=RequirementPriority.CRITICAL,
            confidence=0.95
        ),
    ]


@pytest.fixture
def sample_risks():
    """Create sample risks for testing."""
    return [
        Risk(
            id="risk-1",
            rfp_id="rfp-123",
            clause_text="Test risk",
            category=RiskCategory.LEGAL,
            severity=RiskSeverity.CRITICAL,
            confidence=0.95,
            recommendation="Test recommendation",
            acknowledged=True  # Acknowledged to allow draft generation
        ),
    ]


@pytest.fixture
def sample_acknowledged_risks():
    """Create sample risks that are all acknowledged."""
    return [
        Risk(
            id="risk-1",
            rfp_id="rfp-123",
            clause_text="Test risk",
            category=RiskCategory.LEGAL,
            severity=RiskSeverity.CRITICAL,
            confidence=0.95,
            recommendation="Test recommendation",
            acknowledged=True
        ),
        Risk(
            id="risk-2",
            rfp_id="rfp-123",
            clause_text="Another risk",
            category=RiskCategory.FINANCIAL,
            severity=RiskSeverity.HIGH,
            confidence=0.85,
            recommendation="Another recommendation",
            acknowledged=True
        ),
    ]


class TestDraftGenerator:
    """Test DraftGenerator service."""
    
    def test_draft_generator_initialization(self, mock_llm_client):
        """Test DraftGenerator initialization."""
        generator = DraftGenerator(llm_client=mock_llm_client)
        assert generator.llm_client == mock_llm_client
        assert generator.temperature == 0.7
        assert len(generator.STANDARD_SECTIONS) == 6
    
    def test_draft_generator_initialization_default_client(self):
        """Test DraftGenerator initialization with default client."""
        with patch('services.draft_generator.create_llm_client') as mock_create:
            mock_client = Mock()
            mock_create.return_value = mock_client
            generator = DraftGenerator()
            assert generator.llm_client == mock_client
    
    def test_generate_draft_success(self, mock_llm_client, sample_rfp, sample_requirements, sample_acknowledged_risks):
        """Test successful draft generation."""
        generator = DraftGenerator(llm_client=mock_llm_client)
        
        draft = generator.generate_draft(
            rfp=sample_rfp,
            requirements=sample_requirements,
            risks=sample_acknowledged_risks,
            word_count=2000
        )
        
        assert isinstance(draft, Draft)
        assert draft.rfp_id == "rfp-123"
        assert draft.word_count > 0
        assert len(draft.sections) > 0
        assert draft.status == DraftStatus.GENERATED
        assert draft.generated_by == GenerationMethod.AI
        assert draft.generation_time is not None
        mock_llm_client.generate.assert_called_once()
    
    def test_generate_draft_with_critical_unacknowledged_risks(self, mock_llm_client, sample_rfp, sample_requirements):
        """Test that draft generation fails if critical risks not acknowledged."""
        unacknowledged_risks = [
            Risk(
                id="risk-1",
                rfp_id="rfp-123",
                clause_text="Critical risk",
                category=RiskCategory.LEGAL,
                severity=RiskSeverity.CRITICAL,
                confidence=0.95,
                recommendation="Test",
                acknowledged=False  # Not acknowledged!
            )
        ]
        
        generator = DraftGenerator(llm_client=mock_llm_client)
        
        with pytest.raises(ValueError, match="critical risk.*not acknowledged"):
            generator.generate_draft(
                rfp=sample_rfp,
                requirements=sample_requirements,
                risks=unacknowledged_risks
            )
    
    def test_generate_draft_allows_acknowledged_critical_risks(self, mock_llm_client, sample_rfp, sample_requirements):
        """Test that draft generation succeeds if critical risks are acknowledged."""
        acknowledged_risks = [
            Risk(
                id="risk-1",
                rfp_id="rfp-123",
                clause_text="Critical risk",
                category=RiskCategory.LEGAL,
                severity=RiskSeverity.CRITICAL,
                confidence=0.95,
                recommendation="Test",
                acknowledged=True  # Acknowledged!
            )
        ]
        
        generator = DraftGenerator(llm_client=mock_llm_client)
        
        draft = generator.generate_draft(
            rfp=sample_rfp,
            requirements=sample_requirements,
            risks=acknowledged_risks
        )
        
        assert isinstance(draft, Draft)
    
    def test_generate_draft_allows_non_critical_unacknowledged_risks(self, mock_llm_client, sample_rfp, sample_requirements):
        """Test that non-critical unacknowledged risks don't block generation."""
        non_critical_risks = [
            Risk(
                id="risk-1",
                rfp_id="rfp-123",
                clause_text="High risk",
                category=RiskCategory.FINANCIAL,
                severity=RiskSeverity.HIGH,  # Not critical
                confidence=0.85,
                recommendation="Test",
                acknowledged=False  # Not acknowledged, but not critical
            )
        ]
        
        generator = DraftGenerator(llm_client=mock_llm_client)
        
        draft = generator.generate_draft(
            rfp=sample_rfp,
            requirements=sample_requirements,
            risks=non_critical_risks
        )
        
        assert isinstance(draft, Draft)
    
    def test_generate_draft_word_count_validation(self, mock_llm_client, sample_rfp, sample_requirements, sample_acknowledged_risks):
        """Test word count validation."""
        generator = DraftGenerator(llm_client=mock_llm_client)
        
        # Test minimum word count
        with pytest.raises(ValueError, match="Word count must be between"):
            generator.generate_draft(
                rfp=sample_rfp,
                requirements=sample_requirements,
                risks=sample_acknowledged_risks,
                word_count=100  # Too low
            )
        
        # Test maximum word count
        with pytest.raises(ValueError, match="Word count must be between"):
            generator.generate_draft(
                rfp=sample_rfp,
                requirements=sample_requirements,
                risks=sample_acknowledged_risks,
                word_count=20000  # Too high
            )
    
    def test_generate_draft_custom_instructions(self, mock_llm_client, sample_rfp, sample_requirements, sample_acknowledged_risks):
        """Test draft generation with custom instructions."""
        generator = DraftGenerator(llm_client=mock_llm_client)
        
        draft = generator.generate_draft(
            rfp=sample_rfp,
            requirements=sample_requirements,
            risks=sample_acknowledged_risks,
            instructions="Use formal tone and focus on security",
            tone="formal",
            audience="enterprise"
        )
        
        assert isinstance(draft, Draft)
        call_args = mock_llm_client.generate.call_args
        prompt = call_args[0][0]
        assert "formal" in prompt.lower()
        assert "enterprise" in prompt.lower()
    
    def test_generate_draft_parses_sections(self, mock_llm_client, sample_rfp, sample_requirements, sample_acknowledged_risks):
        """Test that draft sections are parsed correctly."""
        generator = DraftGenerator(llm_client=mock_llm_client)
        
        draft = generator.generate_draft(
            rfp=sample_rfp,
            requirements=sample_requirements,
            risks=sample_acknowledged_risks
        )
        
        assert len(draft.sections) > 0
        # Check that sections have proper structure
        for section in draft.sections:
            assert section.title != ""
            assert section.content != ""
            assert section.word_count > 0
    
    def test_generate_draft_calculates_completeness(self, mock_llm_client, sample_rfp, sample_requirements, sample_acknowledged_risks):
        """Test that completeness score is calculated."""
        generator = DraftGenerator(llm_client=mock_llm_client)
        
        draft = generator.generate_draft(
            rfp=sample_rfp,
            requirements=sample_requirements,
            risks=sample_acknowledged_risks
        )
        
        assert draft.completeness_score is not None
        assert 0.0 <= draft.completeness_score <= 1.0
    
    def test_regenerate_section_success(self, mock_llm_client, sample_rfp, sample_requirements, sample_acknowledged_risks):
        """Test successful section regeneration."""
        generator = DraftGenerator(llm_client=mock_llm_client)
        
        # Generate initial draft
        draft = generator.generate_draft(
            rfp=sample_rfp,
            requirements=sample_requirements,
            risks=sample_acknowledged_risks
        )
        
        # Regenerate a section
        section = generator.regenerate_section(
            draft=draft,
            section_type="executive_summary",
            rfp=sample_rfp,
            requirements=sample_requirements,
            risks=sample_acknowledged_risks
        )
        
        assert isinstance(section, DraftSection)
        assert section.section_type == "executive_summary"
        assert section.content != ""
        assert section.word_count > 0
        assert section.user_edited is False  # Reset after regeneration
    
    def test_regenerate_section_not_found(self, mock_llm_client, sample_rfp, sample_requirements, sample_acknowledged_risks):
        """Test regenerating a section that doesn't exist."""
        generator = DraftGenerator(llm_client=mock_llm_client)
        
        # Generate draft with minimal content
        mock_llm_client.generate.return_value = "# Executive Summary\n\nContent"
        draft = generator.generate_draft(
            rfp=sample_rfp,
            requirements=sample_requirements,
            risks=sample_acknowledged_risks
        )
        
        # Try to regenerate non-existent section
        with pytest.raises(ValueError, match="Section.*not found"):
            generator.regenerate_section(
                draft=draft,
                section_type="nonexistent_section",
                rfp=sample_rfp,
                requirements=sample_requirements,
                risks=sample_acknowledged_risks
            )
    
    def test_build_rfp_info(self, mock_llm_client, sample_rfp):
        """Test building RFP information summary."""
        generator = DraftGenerator(llm_client=mock_llm_client)
        rfp_info = generator._build_rfp_info(sample_rfp)
        
        assert "Test RFP" in rfp_info
        assert "test_rfp.pdf" in rfp_info
        assert "test RFP document" in rfp_info
    
    def test_build_requirements_summary(self, mock_llm_client, sample_requirements):
        """Test building requirements summary."""
        generator = DraftGenerator(llm_client=mock_llm_client)
        summary = generator._build_requirements_summary(sample_requirements)
        
        assert "1" in summary or "Total Requirements" in summary
        assert "technical" in summary.lower() or "Technical" in summary
    
    def test_build_requirements_summary_empty(self, mock_llm_client):
        """Test building requirements summary with no requirements."""
        generator = DraftGenerator(llm_client=mock_llm_client)
        summary = generator._build_requirements_summary([])
        
        assert "no requirements" in summary.lower() or "requirements extracted" in summary.lower()
    
    def test_build_service_matches_summary(self, mock_llm_client):
        """Test building service matches summary."""
        generator = DraftGenerator(llm_client=mock_llm_client)
        
        # Mock service matches with new ServiceMatch structure
        class MockServiceMatch:
            def __init__(self, name="Test Service", score=0.95, approved=True):
                self.service_name = name
                self.score = score
                self.approved = approved
                self.requirement_description = "Test requirement description"
                self.reasoning = "Strong match based on keywords"
        
        # Create high-confidence approved matches (>80%)
        service_matches = [
            MockServiceMatch(name="Cloud Service", score=0.92, approved=True),
            MockServiceMatch(name="Dev Service", score=0.88, approved=True),
            MockServiceMatch(name="QA Service", score=0.70, approved=False),  # Low score, not approved
        ]
        summary = generator._build_service_matches_summary(service_matches)
        
        # Should only include approved high-confidence matches (>80%)
        assert "Approved Service Matches" in summary or "2" in summary
        assert "Cloud Service" in summary or "Dev Service" in summary
    
    def test_build_service_matches_summary_empty(self, mock_llm_client):
        """Test building service matches summary with no matches."""
        generator = DraftGenerator(llm_client=mock_llm_client)
        summary = generator._build_service_matches_summary([])
        
        assert "No service matches" in summary.lower() or "standard service" in summary.lower()
    
    def test_build_risks_summary(self, mock_llm_client, sample_risks):
        """Test building risks summary."""
        generator = DraftGenerator(llm_client=mock_llm_client)
        summary = generator._build_risks_summary(sample_risks)
        
        assert "1" in summary or "Total Risks" in summary
        assert "critical" in summary.lower() or "Critical" in summary
    
    def test_build_risks_summary_empty(self, mock_llm_client):
        """Test building risks summary with no risks."""
        generator = DraftGenerator(llm_client=mock_llm_client)
        summary = generator._build_risks_summary([])
        
        assert "no risks" in summary.lower() or "risks detected" in summary.lower()
    
    def test_clean_draft_content(self, mock_llm_client):
        """Test cleaning draft content."""
        generator = DraftGenerator(llm_client=mock_llm_client)
        
        # Test with markdown code blocks
        content_with_blocks = "```\nActual content\n```"
        cleaned = generator._clean_draft_content(content_with_blocks)
        assert "```" not in cleaned
        assert "Actual content" in cleaned
        
        # Test with leading/trailing whitespace
        content_with_whitespace = "   \nContent\n   "
        cleaned = generator._clean_draft_content(content_with_whitespace)
        assert cleaned == "Content"
    
    def test_parse_sections(self, mock_llm_client):
        """Test parsing sections from draft content."""
        generator = DraftGenerator(llm_client=mock_llm_client)
        
        content = """# Executive Summary

Summary content here.

## Approach

Approach content here.

## Services

Services content here."""
        
        sections = generator._parse_sections(content)
        
        assert len(sections) >= 2
        assert any(s.section_type == "executive_summary" for s in sections)
        assert any(s.section_type == "approach" for s in sections)
    
    def test_parse_sections_no_headings(self, mock_llm_client):
        """Test parsing sections when content has no headings."""
        generator = DraftGenerator(llm_client=mock_llm_client)
        
        content = "Just plain content without any headings."
        sections = generator._parse_sections(content)
        
        assert len(sections) == 1
        assert sections[0].section_type == "executive_summary"
        assert sections[0].content == content
    
    def test_map_title_to_section_type(self, mock_llm_client):
        """Test mapping section titles to section types."""
        generator = DraftGenerator(llm_client=mock_llm_client)
        
        assert generator._map_title_to_section_type("Executive Summary") == "executive_summary"
        assert generator._map_title_to_section_type("Approach") == "approach"
        assert generator._map_title_to_section_type("Services & Solutions") == "services"
        assert generator._map_title_to_section_type("Timeline") == "timeline"
        assert generator._map_title_to_section_type("Pricing") == "pricing"
        assert generator._map_title_to_section_type("Risk Mitigation") == "risk_mitigation"
        assert generator._map_title_to_section_type("Unknown Section") == "other"
    
    def test_get_other_sections_content(self, mock_llm_client, sample_rfp, sample_requirements, sample_acknowledged_risks):
        """Test getting other sections content for context."""
        generator = DraftGenerator(llm_client=mock_llm_client)
        
        draft = generator.generate_draft(
            rfp=sample_rfp,
            requirements=sample_requirements,
            risks=sample_acknowledged_risks
        )
        
        other_content = generator._get_other_sections_content(draft, "executive_summary")
        
        assert "executive_summary" not in other_content.lower() or len(draft.sections) == 1
        if len(draft.sections) > 1:
            assert len(other_content) > 0
    
    def test_calculate_completeness(self, mock_llm_client):
        """Test calculating draft completeness."""
        generator = DraftGenerator(llm_client=mock_llm_client)
        
        # Test with all required sections
        sections = [
            DraftSection(section_type="executive_summary", title="Executive Summary"),
            DraftSection(section_type="services", title="Services"),
            DraftSection(section_type="pricing", title="Pricing"),
        ]
        completeness = generator._calculate_completeness(sections)
        assert completeness == 1.0
        
        # Test with missing sections
        sections = [
            DraftSection(section_type="executive_summary", title="Executive Summary"),
        ]
        completeness = generator._calculate_completeness(sections)
        assert completeness < 1.0
    
    def test_generate_draft_error_handling(self, mock_llm_client, sample_rfp, sample_requirements, sample_acknowledged_risks):
        """Test error handling during draft generation."""
        mock_llm_client.generate.side_effect = Exception("LLM error")
        generator = DraftGenerator(llm_client=mock_llm_client)
        
        with pytest.raises(Exception):
            generator.generate_draft(
                rfp=sample_rfp,
                requirements=sample_requirements,
                risks=sample_acknowledged_risks
            )
    
    def test_regenerate_section_error_handling(self, mock_llm_client, sample_rfp, sample_requirements, sample_acknowledged_risks):
        """Test error handling during section regeneration."""
        generator = DraftGenerator(llm_client=mock_llm_client)
        
        draft = generator.generate_draft(
            rfp=sample_rfp,
            requirements=sample_requirements,
            risks=sample_acknowledged_risks
        )
        
        mock_llm_client.generate.side_effect = Exception("LLM error")
        
        with pytest.raises(Exception):
            generator.regenerate_section(
                draft=draft,
                section_type="executive_summary",
                rfp=sample_rfp,
                requirements=sample_requirements,
                risks=sample_acknowledged_risks
            )

