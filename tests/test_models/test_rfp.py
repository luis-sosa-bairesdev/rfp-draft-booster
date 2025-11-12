"""
Tests for RFP model.
"""

import pytest
from datetime import datetime, timedelta
from models import RFP, RFPStatus


class TestRFPModel:
    """Test RFP data model."""
    
    def test_create_rfp_with_defaults(self):
        """Test creating RFP with default values."""
        rfp = RFP()
        
        assert rfp.id.startswith("rfp-")
        assert rfp.status == RFPStatus.UPLOADED
        assert rfp.file_size == 0
        assert isinstance(rfp.upload_date, datetime)
    
    def test_create_rfp_with_values(self):
        """Test creating RFP with specific values."""
        rfp = RFP(
            id="test-rfp-1",
            title="Test RFP",
            file_name="test.pdf",
            file_size=1024000,
            client_name="Test Corp"
        )
        
        assert rfp.id == "test-rfp-1"
        assert rfp.title == "Test RFP"
        assert rfp.file_name == "test.pdf"
        assert rfp.file_size == 1024000
        assert rfp.client_name == "Test Corp"
    
    def test_is_overdue_with_past_deadline(self):
        """Test is_overdue returns True for past deadline."""
        past_deadline = datetime.now() - timedelta(days=1)
        rfp = RFP(deadline=past_deadline)
        
        assert rfp.is_overdue() is True
    
    def test_is_overdue_with_future_deadline(self):
        """Test is_overdue returns False for future deadline."""
        future_deadline = datetime.now() + timedelta(days=1)
        rfp = RFP(deadline=future_deadline)
        
        assert rfp.is_overdue() is False
    
    def test_is_overdue_without_deadline(self):
        """Test is_overdue returns False when no deadline."""
        rfp = RFP(deadline=None)
        
        assert rfp.is_overdue() is False
    
    def test_days_until_deadline(self):
        """Test days_until_deadline calculation."""
        future_deadline = datetime.now() + timedelta(days=5)
        rfp = RFP(deadline=future_deadline)
        
        days = rfp.days_until_deadline()
        assert 4 <= days <= 5  # Allow for small time differences
    
    def test_days_until_deadline_without_deadline(self):
        """Test days_until_deadline returns -1 when no deadline."""
        rfp = RFP(deadline=None)
        
        assert rfp.days_until_deadline() == -1
    
    def test_size_mb(self):
        """Test size_mb conversion."""
        rfp = RFP(file_size=2 * 1024 * 1024)  # 2MB
        
        assert rfp.size_mb() == 2.0
    
    def test_can_process_when_ready(self):
        """Test can_process returns True when RFP is ready."""
        rfp = RFP(
            status=RFPStatus.UPLOADED,
            file_path="/path/to/file.pdf",
            file_size=1024
        )
        
        assert rfp.can_process() is True
    
    def test_can_process_when_not_ready(self):
        """Test can_process returns False when RFP is not ready."""
        rfp = RFP(
            status=RFPStatus.PROCESSING,
            file_path="",
            file_size=0
        )
        
        assert rfp.can_process() is False
    
    def test_can_process_with_error_status(self):
        """Test can_process returns True for ERROR status."""
        rfp = RFP(
            status=RFPStatus.ERROR,
            file_path="/path/to/file.pdf",
            file_size=1024
        )
        
        assert rfp.can_process() is True

