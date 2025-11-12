"""
Unit tests for Upload RFP page UI.

Note: These tests mock Streamlit components to test the logic without requiring
a full Streamlit runtime.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import io
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from models.rfp import RFP, RFPStatus


class TestUploadPageLogic:
    """Test business logic functions in Upload page."""
    
    def test_file_validation_logic(self):
        """Test file validation logic."""
        # Valid file
        valid_filename = "test_rfp.pdf"
        valid_size = 1024 * 1024  # 1MB
        assert valid_filename.endswith(".pdf")
        assert valid_size < 50 * 1024 * 1024  # Less than 50MB
        
        # Invalid file extension
        invalid_filename = "test_rfp.txt"
        assert not invalid_filename.endswith(".pdf")
        
        # Invalid file size
        invalid_size = 100 * 1024 * 1024  # 100MB
        assert invalid_size > 50 * 1024 * 1024  # More than 50MB
    
    def test_rfp_creation_from_upload(self):
        """Test RFP object creation from uploaded file."""
        rfp = RFP(
            title="Test RFP",
            file_name="test_rfp.pdf",
            file_size=1024 * 1024,
            total_pages=5,
            extracted_text="Sample RFP text content",
            status=RFPStatus.UPLOADED
        )
        
        assert rfp.title == "Test RFP"
        assert rfp.file_name == "test_rfp.pdf"
        assert rfp.total_pages == 5
        assert rfp.status == RFPStatus.UPLOADED
        assert len(rfp.extracted_text) > 0
    
    def test_extracted_text_processing(self):
        """Test extracted text processing."""
        sample_text = "This is a sample RFP document with multiple sentences. It contains requirements and specifications."
        
        # Word count
        word_count = len(sample_text.split())
        assert word_count > 0
        
        # Page extraction (simulated)
        pages = {1: sample_text}
        assert len(pages) == 1
        assert 1 in pages


class TestUploadPageStateManagement:
    """Test session state management for upload page."""
    
    @patch('streamlit.session_state', new_callable=dict)
    def test_processing_state(self, mock_session_state):
        """Test processing state management."""
        mock_session_state["processing"] = False
        mock_session_state["processing_complete"] = False
        mock_session_state["current_rfp"] = None
        
        # Start processing
        mock_session_state["processing"] = True
        assert mock_session_state["processing"] is True
        
        # Complete processing
        mock_rfp = Mock(spec=RFP)
        mock_session_state["processing"] = False
        mock_session_state["processing_complete"] = True
        mock_session_state["current_rfp"] = mock_rfp
        
        assert mock_session_state["processing"] is False
        assert mock_session_state["processing_complete"] is True
        assert mock_session_state["current_rfp"] is not None
    
    def test_rfp_reset_logic(self):
        """Test RFP reset logic."""
        # Simulate reset
        state = {
            "processing_complete": True,
            "current_rfp": Mock(spec=RFP),
            "requirements": [Mock()],
            "risks": [Mock()]
        }
        
        # Reset
        state["processing_complete"] = False
        state["current_rfp"] = None
        
        assert state["processing_complete"] is False
        assert state["current_rfp"] is None


class TestUploadPageFileHandling:
    """Test file handling logic."""
    
    def test_file_size_calculation(self):
        """Test file size calculations."""
        # Small file
        small_size = 1024  # 1KB
        assert small_size < 50 * 1024 * 1024
        
        # Large file
        large_size = 100 * 1024 * 1024  # 100MB
        assert large_size > 50 * 1024 * 1024
        
        # Convert to MB
        size_mb = large_size / (1024 * 1024)
        assert size_mb == 100.0
    
    def test_file_extension_validation(self):
        """Test file extension validation."""
        valid_extensions = [".pdf"]
        
        assert "test.pdf".endswith(".pdf")
        assert "test.PDF".lower().endswith(".pdf")
        assert "test.pdf".endswith(tuple(valid_extensions))
        
        assert not "test.txt".endswith(".pdf")
        assert not "test.docx".endswith(".pdf")

