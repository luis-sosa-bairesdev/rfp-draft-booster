"""
Unit tests for AI Assistant service.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from models import RFP, Requirement, Risk, RequirementCategory, RequirementPriority, RiskCategory, RiskSeverity
from services.ai_assistant import AIAssistant, AIMessage
from services.llm_client import LLMClient, LLMProvider


@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client."""
    client = Mock(spec=LLMClient)
    client.provider = LLMProvider.GEMINI
    client.generate = Mock(return_value="This is a helpful response about RFPs.")
    return client


@pytest.fixture
def sample_rfp():
    """Create a sample RFP for testing."""
    rfp = RFP(
        id="rfp-123",
        file_name="test_rfp.pdf",
        extracted_text="This is a test RFP document with some requirements and risks."
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
            confidence=0.95,
            page_number=3
        ),
        Requirement(
            id="req-2",
            rfp_id="rfp-123",
            description="Project completion within 60 days",
            category=RequirementCategory.TIMELINE,
            priority=RequirementPriority.HIGH,
            confidence=0.90,
            page_number=5
        ),
    ]


@pytest.fixture
def sample_risks():
    """Create sample risks for testing."""
    return [
        Risk(
            id="risk-1",
            rfp_id="rfp-123",
            clause_text="Vendor assumes all liability",
            category=RiskCategory.LEGAL,
            severity=RiskSeverity.CRITICAL,
            confidence=0.95,
            page_number=12,
            recommendation="Negotiate liability cap",
            alternative_language="Liability limited to contract value"
        ),
        Risk(
            id="risk-2",
            rfp_id="rfp-123",
            clause_text="Payment terms: Net 90 days",
            category=RiskCategory.FINANCIAL,
            severity=RiskSeverity.HIGH,
            confidence=0.85,
            page_number=8,
            recommendation="Negotiate Net 30 terms",
            alternative_language="Payment terms: Net 30 days"
        ),
    ]


class TestAIMessage:
    """Test AIMessage class."""
    
    def test_aimessage_creation(self):
        """Test creating an AIMessage."""
        msg = AIMessage("user", "Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert isinstance(msg.timestamp, datetime)
    
    def test_aimessage_to_dict(self):
        """Test converting AIMessage to dictionary."""
        msg = AIMessage("assistant", "Response")
        msg_dict = msg.to_dict()
        
        assert msg_dict["role"] == "assistant"
        assert msg_dict["content"] == "Response"
        assert "timestamp" in msg_dict


class TestAIAssistant:
    """Test AIAssistant service."""
    
    def test_ai_assistant_initialization(self, mock_llm_client):
        """Test AIAssistant initialization."""
        assistant = AIAssistant(llm_client=mock_llm_client)
        assert assistant.llm_client == mock_llm_client
        assert assistant.temperature == 0.7
        assert len(assistant.conversation_history) == 0
    
    def test_ai_assistant_initialization_default_client(self):
        """Test AIAssistant initialization with default client."""
        with patch('services.ai_assistant.create_llm_client') as mock_create:
            mock_client = Mock()
            mock_create.return_value = mock_client
            assistant = AIAssistant()
            assert assistant.llm_client == mock_client
    
    def test_ask_without_context(self, mock_llm_client):
        """Test asking a question without RFP context."""
        assistant = AIAssistant(llm_client=mock_llm_client)
        
        response = assistant.ask("What is an RFP?")
        
        assert response == "This is a helpful response about RFPs."
        assert len(assistant.conversation_history) == 2  # User + Assistant
        assert assistant.conversation_history[0].role == "user"
        assert assistant.conversation_history[1].role == "assistant"
        mock_llm_client.generate.assert_called_once()
    
    def test_ask_with_rfp_context(self, mock_llm_client, sample_rfp):
        """Test asking a question with RFP context."""
        assistant = AIAssistant(llm_client=mock_llm_client)
        
        response = assistant.ask("What is this RFP about?", rfp=sample_rfp)
        
        assert response == "This is a helpful response about RFPs."
        assert len(assistant.conversation_history) == 2
        # Verify context was included in prompt
        call_args = mock_llm_client.generate.call_args
        assert call_args is not None
        prompt = call_args[0][0]
        assert "Test RFP" in prompt or "test RFP document" in prompt
    
    def test_ask_with_requirements(self, mock_llm_client, sample_rfp, sample_requirements):
        """Test asking a question with requirements context."""
        assistant = AIAssistant(llm_client=mock_llm_client)
        
        response = assistant.ask(
            "How many requirements are there?",
            rfp=sample_rfp,
            requirements=sample_requirements
        )
        
        assert response == "This is a helpful response about RFPs."
        call_args = mock_llm_client.generate.call_args
        prompt = call_args[0][0]
        assert "2" in prompt or "requirements" in prompt.lower()
    
    def test_ask_with_risks(self, mock_llm_client, sample_rfp, sample_risks):
        """Test asking a question with risks context."""
        assistant = AIAssistant(llm_client=mock_llm_client)
        
        response = assistant.ask(
            "What are the critical risks?",
            rfp=sample_rfp,
            risks=sample_risks
        )
        
        assert response == "This is a helpful response about RFPs."
        call_args = mock_llm_client.generate.call_args
        prompt = call_args[0][0]
        assert "risk" in prompt.lower() or "critical" in prompt.lower()
    
    def test_ask_with_full_context(self, mock_llm_client, sample_rfp, sample_requirements, sample_risks):
        """Test asking a question with full context."""
        assistant = AIAssistant(llm_client=mock_llm_client)
        
        response = assistant.ask(
            "Give me a summary of this RFP",
            rfp=sample_rfp,
            requirements=sample_requirements,
            risks=sample_risks
        )
        
        assert response == "This is a helpful response about RFPs."
        call_args = mock_llm_client.generate.call_args
        prompt = call_args[0][0]
        # Verify all context types are included
        assert "RFP" in prompt
        assert "requirements" in prompt.lower() or "2" in prompt
        assert "risk" in prompt.lower() or "critical" in prompt.lower()
    
    def test_ask_conversation_history(self, mock_llm_client):
        """Test that conversation history is maintained."""
        assistant = AIAssistant(llm_client=mock_llm_client)
        
        assistant.ask("First question")
        assistant.ask("Follow-up question")
        
        assert len(assistant.conversation_history) == 4  # 2 user + 2 assistant
        assert assistant.conversation_history[0].content == "First question"
        assert assistant.conversation_history[2].content == "Follow-up question"
    
    def test_ask_error_handling(self, mock_llm_client):
        """Test error handling when LLM fails."""
        mock_llm_client.generate.side_effect = Exception("LLM error")
        assistant = AIAssistant(llm_client=mock_llm_client)
        
        response = assistant.ask("Test question")
        
        assert "error" in response.lower() or "apologize" in response.lower()
        assert len(assistant.conversation_history) == 2  # User + error response
    
    def test_clean_response_removes_markdown(self, mock_llm_client):
        """Test that markdown code blocks are removed from responses."""
        mock_llm_client.generate.return_value = "```\nThis is the actual response\n```"
        assistant = AIAssistant(llm_client=mock_llm_client)
        
        response = assistant.ask("Test")
        
        assert "```" not in response
        assert "This is the actual response" in response
    
    def test_clear_history(self, mock_llm_client):
        """Test clearing conversation history."""
        assistant = AIAssistant(llm_client=mock_llm_client)
        assistant.ask("Question 1")
        assistant.ask("Question 2")
        
        assert len(assistant.conversation_history) == 4
        
        assistant.clear_history()
        
        assert len(assistant.conversation_history) == 0
    
    def test_get_history(self, mock_llm_client):
        """Test getting conversation history as dictionaries."""
        assistant = AIAssistant(llm_client=mock_llm_client)
        assistant.ask("Test question")
        
        history = assistant.get_history()
        
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "assistant"
        assert "timestamp" in history[0]
        assert "timestamp" in history[1]
    
    def test_get_last_response(self, mock_llm_client):
        """Test getting the last assistant response."""
        assistant = AIAssistant(llm_client=mock_llm_client)
        assistant.ask("Question 1")
        assistant.ask("Question 2")
        
        last_response = assistant.get_last_response()
        
        assert last_response == "This is a helpful response about RFPs."
    
    def test_get_last_response_no_history(self, mock_llm_client):
        """Test getting last response when no history exists."""
        assistant = AIAssistant(llm_client=mock_llm_client)
        
        last_response = assistant.get_last_response()
        
        assert last_response is None
    
    def test_build_context_rfp_only(self, mock_llm_client, sample_rfp):
        """Test building context with only RFP."""
        assistant = AIAssistant(llm_client=mock_llm_client)
        context = assistant._build_context(sample_rfp, None, None)
        
        assert context["rfp_summary"] != ""
        assert "Test RFP" in context["rfp_summary"]
        assert context["requirements_count"] == 0
        assert context["risks_count"] == 0
    
    def test_build_context_with_requirements(self, mock_llm_client, sample_requirements):
        """Test building context with requirements."""
        assistant = AIAssistant(llm_client=mock_llm_client)
        context = assistant._build_context(None, sample_requirements, None)
        
        assert context["requirements_count"] == 2
        assert "technical" in context["requirements_summary"].lower() or "2" in context["requirements_summary"]
    
    def test_build_context_with_risks(self, mock_llm_client, sample_risks):
        """Test building context with risks."""
        assistant = AIAssistant(llm_client=mock_llm_client)
        context = assistant._build_context(None, None, sample_risks)
        
        assert context["risks_count"] == 2
        assert len(context["critical_risks"]) == 1  # One critical risk
        assert context["critical_risks"][0]["category"] == "legal"
    
    def test_build_context_critical_risks_limit(self, mock_llm_client):
        """Test that critical risks are limited to top 5."""
        # Create 10 critical risks
        critical_risks = [
            Risk(
                id=f"risk-{i}",
                rfp_id="rfp-123",
                clause_text=f"Risk {i}",
                category=RiskCategory.LEGAL,
                severity=RiskSeverity.CRITICAL,
                confidence=0.95,
                recommendation="Test"
            )
            for i in range(10)
        ]
        
        assistant = AIAssistant(llm_client=mock_llm_client)
        context = assistant._build_context(None, None, critical_risks)
        
        assert len(context["critical_risks"]) == 5  # Limited to 5
    
    def test_temperature_parameter(self, mock_llm_client):
        """Test that temperature parameter is used."""
        assistant = AIAssistant(llm_client=mock_llm_client, temperature=0.9)
        assistant.ask("Test")
        
        call_args = mock_llm_client.generate.call_args
        assert call_args is not None
        # Check that temperature was passed (either as kwarg or in the call)
        kwargs = call_args[1] if len(call_args) > 1 else {}
        if "temperature" in kwargs:
            assert kwargs["temperature"] == 0.9

