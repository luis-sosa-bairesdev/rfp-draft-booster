"""Extended tests for session utilities to improve coverage."""

from unittest.mock import MagicMock, patch
from models import RFP, Requirement, Risk, Draft, Service
from models.requirement import RequirementCategory, RequirementPriority


class TestSessionInitialization:
    """Test session state initialization."""
    
    def test_init_session_state_creates_all_variables(self):
        """Test that init_session_state creates all required variables."""
        mock_st = MagicMock()
        mock_st.session_state = {}
        
        with patch('utils.session.st', mock_st):
            from utils.session import init_session_state
            
            init_session_state()
            
            # Verify all keys are created
            expected_keys = [
                'rfp', 'requirements', 'services', 'service_matches',
                'approved_matches', 'risks', 'draft', 'editing_mode',
                'processing', 'show_ai_assistant', 'config'
            ]
            
            for key in expected_keys:
                assert key in mock_st.session_state, f"Key '{key}' not initialized"
    
    def test_init_session_state_idempotent(self):
        """Test that calling init_session_state multiple times doesn't overwrite existing values."""
        mock_st = MagicMock()
        
        # Pre-populate with some data
        test_rfp = RFP(id="test-001", file_name="test.pdf")
        mock_st.session_state = {
            'rfp': test_rfp,
            'requirements': [Requirement(id="req-1", description="Test", category=RequirementCategory.TECHNICAL, priority=RequirementPriority.HIGH)]
        }
        
        with patch('utils.session.st', mock_st):
            from utils.session import init_session_state
            
            init_session_state()
            
            # Verify existing values are preserved
            assert mock_st.session_state['rfp'] == test_rfp
            assert len(mock_st.session_state['requirements']) == 1


class TestSessionReset:
    """Test session reset functionality."""
    
    def test_reset_session_clears_all_data(self):
        """Test that reset_session clears all RFP-related data."""
        mock_st = MagicMock()
        
        # Pre-populate with data
        mock_st.session_state = {
            'rfp': RFP(id="test-001", file_name="test.pdf"),
            'requirements': [Requirement(id="req-1", description="Test", category=RequirementCategory.TECHNICAL, priority=RequirementPriority.HIGH)],
            'services': [],  # Empty services list
            'service_matches': [{'score': 0.9}],
            'approved_matches': [{'score': 0.9}],
            'risks': [],
            'draft': None,
            'editing_mode': True,
            'processing': True
        }
        
        with patch('utils.session.st', mock_st):
            from utils.session import reset_session
            
            reset_session()
            
            # Verify all are reset
            assert mock_st.session_state['rfp'] is None
            assert mock_st.session_state['requirements'] == []
            assert mock_st.session_state['services'] == []
            assert mock_st.session_state['service_matches'] == []
            assert mock_st.session_state['approved_matches'] == []
            assert mock_st.session_state['risks'] == []
            assert mock_st.session_state['draft'] is None
            assert mock_st.session_state['editing_mode'] is False
            assert mock_st.session_state['processing'] is False


class TestApprovedMatches:
    """Test approved matches functionality."""
    
    def test_get_approved_matches_empty(self):
        """Test get_approved_matches when no matches exist."""
        mock_st = MagicMock()
        mock_st.session_state = {'service_matches': []}
        
        with patch('utils.session.st', mock_st):
            from utils.session import get_approved_matches
            
            result = get_approved_matches()
            assert result == []
    
    def test_get_approved_matches_filters_correctly(self):
        """Test get_approved_matches filters only approved matches."""
        # Create mock ServiceMatch objects
        class MockMatch:
            def __init__(self, approved):
                self.approved = approved
        
        mock_st = MagicMock()
        mock_st.session_state = {
            'service_matches': [
                MockMatch(approved=True),
                MockMatch(approved=False),
                MockMatch(approved=True),
            ]
        }
        
        with patch('utils.session.st', mock_st):
            from utils.session import get_approved_matches
            
            result = get_approved_matches()
            assert len(result) == 2
            assert all(m.approved for m in result)
    
    def test_update_approved_matches_syncs_state(self):
        """Test update_approved_matches syncs approved_matches with service_matches."""
        class MockMatch:
            def __init__(self, approved):
                self.approved = approved
        
        mock_st = MagicMock()
        mock_st.session_state = {
            'service_matches': [
                MockMatch(approved=True),
                MockMatch(approved=False),
                MockMatch(approved=True),
            ],
            'approved_matches': []  # Start empty
        }
        
        with patch('utils.session.st', mock_st):
            from utils.session import update_approved_matches
            
            update_approved_matches()
            
            # Verify approved_matches was updated
            assert len(mock_st.session_state['approved_matches']) == 2


class TestCurrentRFPHelpers:
    """Test RFP helper functions."""
    
    def test_get_current_rfp_returns_existing(self):
        """Test get_current_rfp returns RFP when it exists."""
        test_rfp = RFP(id="test-001", file_name="test.pdf")
        mock_st = MagicMock()
        mock_st.session_state = {'rfp': test_rfp}
        
        with patch('utils.session.st', mock_st):
            from utils.session import get_current_rfp
            
            result = get_current_rfp()
            assert result == test_rfp
    
    def test_has_current_rfp_true_when_exists(self):
        """Test has_current_rfp returns True when RFP exists."""
        test_rfp = RFP(id="test-001", file_name="test.pdf")
        mock_st = MagicMock()
        mock_st.session_state = {'rfp': test_rfp}
        
        with patch('utils.session.st', mock_st):
            from utils.session import has_current_rfp
            
            result = has_current_rfp()
            assert result is True

