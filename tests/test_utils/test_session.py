"""
Unit tests for session utilities.

Tests cover:
- Session helper functions
"""

from unittest.mock import MagicMock, patch
from models import RFP


class TestSessionFunctionsExist:
    """Test session functions exist and are callable."""
    
    def test_all_functions_callable(self):
        """Test that all session functions can be imported and are callable."""
        from utils.session import (
            init_session_state,
            reset_session,
            get_current_rfp,
            set_current_rfp,
            has_current_rfp,
            get_approved_matches,
            update_approved_matches
        )
        
        assert callable(init_session_state)
        assert callable(reset_session)
        assert callable(get_current_rfp)
        assert callable(set_current_rfp)
        assert callable(has_current_rfp)
        assert callable(get_approved_matches)
        assert callable(update_approved_matches)


class TestSessionWithMocks:
    """Test session functions with mocked streamlit."""
    
    def test_get_current_rfp_when_none(self):
        """Test getting RFP when none exists."""
        mock_st = MagicMock()
        mock_st.session_state = {}
        
        with patch('utils.session.st', mock_st):
            from utils.session import get_current_rfp
            result = get_current_rfp()
            assert result is None
    
    def test_has_current_rfp_when_false(self):
        """Test has_current_rfp when no RFP."""
        mock_st = MagicMock()
        mock_st.session_state = {}
        
        with patch('utils.session.st', mock_st):
            from utils.session import has_current_rfp
            result = has_current_rfp()
            assert result is False
    
    def test_set_current_rfp(self):
        """Test setting current RFP."""
        mock_st = MagicMock()
        mock_st.session_state = {}
        
        with patch('utils.session.st', mock_st):
            from utils.session import set_current_rfp
            
            rfp = RFP(id="test-001", file_name="test.pdf")
            set_current_rfp(rfp)
            
            assert "rfp" in mock_st.session_state
            assert mock_st.session_state["rfp"] == rfp
