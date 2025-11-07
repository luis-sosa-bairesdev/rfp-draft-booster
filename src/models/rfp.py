"""RFP data model."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4


class RFPStatus(Enum):
    """RFP processing status."""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class RFP:
    """Request for Proposal document."""
    
    # Core identifiers
    id: str = field(default_factory=lambda: f"rfp-{uuid4()}")
    title: str = ""
    file_name: str = ""
    
    # File metadata
    file_size: int = 0
    file_path: str = ""
    total_pages: int = 0
    
    # Client information
    client_name: str = ""
    client_industry: Optional[str] = None
    client_size: Optional[str] = None
    
    # Timeline
    upload_date: datetime = field(default_factory=datetime.now)
    deadline: Optional[datetime] = None
    processing_start: Optional[datetime] = None
    processing_end: Optional[datetime] = None
    processing_time: Optional[float] = None
    
    # Status & processing
    status: RFPStatus = RFPStatus.UPLOADED
    error_message: Optional[str] = None
    extracted_text: Optional[str] = None
    
    # User & ownership
    uploaded_by: str = ""
    assigned_to: Optional[str] = None
    team: Optional[str] = None
    
    def is_overdue(self) -> bool:
        """Check if RFP deadline has passed."""
        if not self.deadline:
            return False
        return datetime.now() > self.deadline
    
    def days_until_deadline(self) -> int:
        """Calculate days remaining until deadline."""
        if not self.deadline:
            return -1
        delta = self.deadline - datetime.now()
        return delta.days
    
    def size_mb(self) -> float:
        """Get file size in megabytes."""
        return self.file_size / (1024 * 1024)
    
    def can_process(self) -> bool:
        """Check if RFP is ready for processing."""
        return (
            self.status in [RFPStatus.UPLOADED, RFPStatus.ERROR]
            and self.file_path
            and self.file_size > 0
        )

