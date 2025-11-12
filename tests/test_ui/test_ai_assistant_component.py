"""UI tests for AI Assistant component."""

import pytest
import streamlit as st
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from components.ai_assistant import (
    render_ai_assistant_button,
    render_ai_assistant_modal,
    init_ai_assistant
)
from models import RFP, Requirement, Risk, RequirementCategory, RequirementPriority, RiskCategory, RiskSeverity
from datetime import datetime


class TestAIAssistantButton:
    """Test AI Assistant button rendering."""
    
    def test_render_button_with_suffix(self):
        """Test button renders with key suffix."""
        with patch('streamlit.button') as mock_button:
            mock_button.return_value = False
            render_ai_assistant_button(key_suffix="test")
            mock_button.assert_called_once()
            call_args = mock_button.call_args
            assert call_args[1]['key'] == "btn_ai_assistant_test"
    
    def test_render_button_without_suffix(self):
        """Test button renders without key suffix."""
        with patch('streamlit.button') as mock_button:
            mock_button.return_value = False
            render_ai_assistant_button()
            mock_button.assert_called_once()
            call_args = mock_button.call_args
            assert call_args[1]['key'] == "btn_ai_assistant"
    
    def test_button_click_sets_state(self):
        """Test button click sets show_ai_assistant state."""
        mock_state = {}
        with patch('streamlit.button') as mock_button, \
             patch('streamlit.session_state', mock_state), \
             patch('streamlit.rerun') as mock_rerun:
            mock_button.return_value = True
            
            render_ai_assistant_button(key_suffix="test")
            
            assert mock_state.get('show_ai_assistant', False) == True


class TestAIAssistantModal:
    """Test AI Assistant modal rendering."""
    
    @pytest.fixture
    def sample_rfp(self):
        """Create sample RFP."""
        return RFP(
            id="test-rfp-1",
            file_name="test.pdf",
            title="Test RFP",
            client_name="Test Client",
            deadline=datetime.now(),
            extracted_text="Sample RFP text",
            uploaded_at=datetime.now()
        )
    
    @pytest.fixture
    def sample_requirements(self):
        """Create sample requirements."""
        return [
            Requirement(
                id="req-1",
                rfp_id="test-rfp-1",
                description="Test requirement",
                category=RequirementCategory.TECHNICAL,
                priority=RequirementPriority.HIGH,
                page_number=1,
                created_at=datetime.now()
            )
        ]
    
    @pytest.fixture
    def sample_risks(self):
        """Create sample risks."""
        return [
            Risk(
                id="risk-1",
                rfp_id="test-rfp-1",
                clause_text="Test risk clause",
                category=RiskCategory.LEGAL,
                severity=RiskSeverity.CRITICAL,
                confidence=0.9,
                page_number=1,
                recommendation="Test recommendation",
                created_at=datetime.now()
            )
        ]
    
    def test_modal_not_rendered_when_closed(self):
        """Test modal doesn't render when show_ai_assistant is False."""
        mock_state = {'show_ai_assistant': False}
        with patch('streamlit.session_state', mock_state), \
             patch('streamlit.markdown') as mock_markdown:
            render_ai_assistant_modal(key_suffix="test")
            # Modal should return early, so markdown should not be called
            # But it might be called for the script, so we check it's minimal
            assert mock_markdown.call_count == 0
    
    def test_modal_rendered_when_open(self):
        """Test modal renders when show_ai_assistant is True."""
        mock_state = {'show_ai_assistant': True, 'requirements': [], 'risks': []}
        with patch('streamlit.session_state', mock_state), \
             patch('streamlit.markdown') as mock_markdown, \
             patch('streamlit.columns') as mock_columns, \
             patch('streamlit.divider') as mock_divider, \
             patch('components.ai_assistant.init_ai_assistant') as mock_init, \
             patch('components.ai_assistant.get_current_rfp') as mock_rfp, \
             patch('streamlit.text_input') as mock_input, \
             patch('streamlit.button') as mock_button:
            
            mock_columns.return_value = [Mock(), Mock()]
            mock_assistant = Mock()
            mock_assistant.get_history.return_value = []
            mock_init.return_value = mock_assistant
            mock_rfp.return_value = None
            mock_input.return_value = ""
            mock_button.return_value = False
            
            render_ai_assistant_modal(key_suffix="test", page_context="test")
            
            # Should render modal elements (markdown for script and content)
            assert mock_markdown.called
    
    def test_modal_with_page_context(self):
        """Test modal passes page_context to assistant."""
        mock_state = {'show_ai_assistant': True, 'requirements': [], 'risks': []}
        with patch('streamlit.session_state', mock_state), \
             patch('streamlit.markdown'), \
             patch('streamlit.columns') as mock_columns, \
             patch('streamlit.divider'), \
             patch('components.ai_assistant.init_ai_assistant') as mock_init, \
             patch('components.ai_assistant.get_current_rfp') as mock_rfp, \
             patch('streamlit.text_input') as mock_input, \
             patch('streamlit.button') as mock_button, \
             patch('streamlit.rerun'):
            
            mock_columns.return_value = [Mock(), Mock()]
            mock_assistant = Mock()
            mock_assistant.get_history.return_value = []
            mock_assistant.ask.return_value = "Test response"
            mock_init.return_value = mock_assistant
            mock_rfp.return_value = None
            mock_input.return_value = "test question"
            
            # Simulate send button click
            def button_side_effect(*args, **kwargs):
                if kwargs.get('key') == 'btn_send_question_test':
                    return True
                return False
            
            mock_button.side_effect = button_side_effect
            
            render_ai_assistant_modal(key_suffix="test", page_context="requirements")
            
            # Verify assistant was initialized
            assert mock_init.called
    
    def test_close_button_closes_modal(self):
        """Test close button sets show_ai_assistant to False."""
        mock_state = {'show_ai_assistant': True, 'requirements': [], 'risks': []}
        
        with patch('streamlit.session_state', mock_state), \
             patch('streamlit.markdown'), \
             patch('streamlit.columns') as mock_columns, \
             patch('streamlit.divider'), \
             patch('components.ai_assistant.init_ai_assistant') as mock_init, \
             patch('components.ai_assistant.get_current_rfp') as mock_rfp, \
             patch('streamlit.text_input') as mock_input, \
             patch('streamlit.button') as mock_button, \
             patch('streamlit.rerun') as mock_rerun:
            
            mock_columns.return_value = [Mock(), Mock()]
            mock_assistant = Mock()
            mock_assistant.get_history.return_value = []
            mock_init.return_value = mock_assistant
            mock_rfp.return_value = None
            mock_input.return_value = ""
            
            # Simulate close button click
            def button_side_effect(*args, **kwargs):
                if kwargs.get('key') == 'btn_close_ai_assistant_test':
                    return True
                return False
            
            mock_button.side_effect = button_side_effect
            
            render_ai_assistant_modal(key_suffix="test")
            
            # Should set show_ai_assistant to False
            assert mock_state.get('show_ai_assistant') == False
            assert mock_rerun.called


class TestAIAssistantInit:
    """Test AI Assistant initialization."""
    
    def test_init_creates_assistant_if_not_exists(self):
        """Test init creates assistant if not in session state."""
        mock_state = {}
        
        with patch('components.ai_assistant.st.session_state', mock_state), \
             patch('services.llm_client.create_llm_client') as mock_create:
            mock_client = Mock()
            mock_create.return_value = mock_client
            
            assistant = init_ai_assistant()
            
            assert 'ai_assistant' in mock_state
            assert mock_state['ai_assistant'] == assistant
    
    def test_init_returns_existing_assistant(self):
        """Test init returns existing assistant from session state."""
        existing_assistant = Mock()
        mock_state = {'ai_assistant': existing_assistant}
        
        with patch('components.ai_assistant.st.session_state', mock_state):
            assistant = init_ai_assistant()
            
            assert assistant == existing_assistant

