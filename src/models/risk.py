"""Risk clause data model."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4


class RiskType(Enum):
    """Risk type categories."""
    LEGAL = "legal"
    FINANCIAL = "financial"
    TIMELINE = "timeline"
    TECHNICAL = "technical"
    COMPLIANCE = "compliance"


class RiskSeverity(Enum):
    """Risk severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DetectionMethod(Enum):
    """How risk was detected."""
    REGEX = "regex"
    LLM = "llm"
    MANUAL = "manual"


@dataclass
class RiskClause:
    """Potentially problematic clause in RFP."""
    
    # Core identifiers
    id: str = field(default_factory=lambda: f"risk-{uuid4()}")
    rfp_id: str = ""
    
    # Classification
    risk_type: RiskType = RiskType.FINANCIAL
    severity: RiskSeverity = RiskSeverity.MEDIUM
    sub_category: Optional[str] = None
    
    # Content
    clause_text: str = ""
    page_number: Optional[int] = None
    section: Optional[str] = None
    
    # Analysis
    risk_description: str = ""
    potential_impact: Optional[str] = None
    recommendation: str = ""
    alternative_language: Optional[str] = None
    
    # Detection
    detected_by: DetectionMethod = DetectionMethod.LLM
    confidence_score: float = 1.0
    detection_pattern: Optional[str] = None
    
    # Status
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledgment_date: Optional[datetime] = None
    resolved: bool = False
    resolution_notes: Optional[str] = None
    
    # Timestamps
    flagged_date: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def is_blocking(self) -> bool:
        """Check if risk blocks draft generation."""
        return self.severity == RiskSeverity.CRITICAL and not self.acknowledged
    
    def requires_manager_approval(self) -> bool:
        """Check if manager approval needed."""
        return self.severity in [RiskSeverity.CRITICAL, RiskSeverity.HIGH]
    
    def acknowledge(self, user_email: str, is_manager: bool = False) -> None:
        """Mark risk as acknowledged."""
        if self.severity == RiskSeverity.CRITICAL and not is_manager:
            raise PermissionError("Only managers can acknowledge critical risks")
        
        self.acknowledged = True
        self.acknowledged_by = user_email
        self.acknowledgment_date = datetime.now()
        self.last_updated = datetime.now()
    
    def mark_resolved(self, notes: str) -> None:
        """Mark risk as resolved with notes."""
        if not self.acknowledged:
            raise ValueError("Risk must be acknowledged before marking resolved")
        
        self.resolved = True
        self.resolution_notes = notes
        self.last_updated = datetime.now()

