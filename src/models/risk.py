"""
Risk data model for RFP risk detection.

This module defines the data structures for storing and managing detected risks
from RFPs, including categorization, severity classification, and recommendations.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


class RiskCategory(str, Enum):
    """Categories for risks detected in RFPs."""
    
    LEGAL = "legal"
    FINANCIAL = "financial"
    TIMELINE = "timeline"
    TECHNICAL = "technical"
    COMPLIANCE = "compliance"


class RiskSeverity(str, Enum):
    """Severity levels for detected risks."""
    
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Risk:
    """
    Represents a single risk detected in an RFP.
    
    Attributes:
        id: Unique identifier for the risk
        rfp_id: ID of the RFP this risk belongs to
        clause_text: The problematic clause text from the RFP
        category: Type of risk (legal, financial, timeline, technical, compliance)
        severity: Severity level (critical, high, medium, low)
        confidence: AI's confidence in this detection (0.0-1.0)
        page_number: Source page number in the RFP (if available)
        recommendation: Mitigation recommendation for this risk
        alternative_language: Suggested alternative clause wording
        acknowledged: Whether a user has acknowledged this risk
        acknowledgment_notes: Notes on how the risk will be addressed
        acknowledged_at: Timestamp when risk was acknowledged
        created_at: Timestamp when risk was detected
        updated_at: Timestamp of last modification
    """
    
    # Core fields
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    rfp_id: str = ""
    clause_text: str = ""
    
    # Classification
    category: RiskCategory = RiskCategory.LEGAL
    severity: RiskSeverity = RiskSeverity.MEDIUM
    
    # Metadata
    confidence: float = 0.0
    page_number: Optional[int] = None
    
    # Recommendations
    recommendation: str = ""
    alternative_language: str = ""
    
    # Acknowledgment
    acknowledged: bool = False
    acknowledgment_notes: str = ""
    acknowledged_at: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate fields after initialization."""
        # Ensure confidence is in valid range
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
        
        # Ensure page_number is positive if provided
        if self.page_number is not None and self.page_number < 1:
            raise ValueError(f"Page number must be >= 1, got {self.page_number}")
        
        # Convert string category/severity to enum if needed
        if isinstance(self.category, str):
            self.category = RiskCategory(self.category.lower())
        
        if isinstance(self.severity, str):
            self.severity = RiskSeverity(self.severity.lower())
    
    def to_dict(self) -> dict:
        """Convert risk to dictionary for serialization."""
        return {
            "id": self.id,
            "rfp_id": self.rfp_id,
            "clause_text": self.clause_text,
            "category": self.category.value,
            "severity": self.severity.value,
            "confidence": self.confidence,
            "page_number": self.page_number,
            "recommendation": self.recommendation,
            "alternative_language": self.alternative_language,
            "acknowledged": self.acknowledged,
            "acknowledgment_notes": self.acknowledgment_notes,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Risk":
        """Create risk from dictionary."""
        # Parse datetime fields
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if isinstance(data.get("updated_at"), str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        if isinstance(data.get("acknowledged_at"), str) and data["acknowledged_at"]:
            data["acknowledged_at"] = datetime.fromisoformat(data["acknowledged_at"])
        
        return cls(**data)
    
    def update(self, **kwargs) -> None:
        """Update risk fields and timestamp."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.updated_at = datetime.now()
    
    def acknowledge(self, notes: str = "") -> None:
        """Acknowledge this risk with optional notes."""
        self.acknowledged = True
        self.acknowledgment_notes = notes
        self.acknowledged_at = datetime.now()
        self.updated_at = datetime.now()
    
    def get_confidence_label(self) -> str:
        """Get human-readable confidence label."""
        if self.confidence >= 0.9:
            return "Very High"
        elif self.confidence >= 0.75:
            return "High"
        elif self.confidence >= 0.5:
            return "Medium"
        else:
            return "Low"
    
    def get_severity_color(self) -> str:
        """Get color code for severity (for UI)."""
        colors = {
            RiskSeverity.CRITICAL: "#FF4444",  # Red
            RiskSeverity.HIGH: "#FF8800",  # Orange
            RiskSeverity.MEDIUM: "#FFBB00",  # Yellow
            RiskSeverity.LOW: "#4CAF50",  # Green
        }
        return colors.get(self.severity, "#808080")
    
    def get_category_icon(self) -> str:
        """Get emoji icon for category (for UI)."""
        icons = {
            RiskCategory.LEGAL: "⚖️",
            RiskCategory.FINANCIAL: "💰",
            RiskCategory.TIMELINE: "⏰",
            RiskCategory.TECHNICAL: "🔧",
            RiskCategory.COMPLIANCE: "📋",
        }
        return icons.get(self.category, "⚠️")


def get_category_display_names() -> dict[str, str]:
    """Get user-friendly category names for UI."""
    return {
        RiskCategory.LEGAL.value: "Legal",
        RiskCategory.FINANCIAL.value: "Financial",
        RiskCategory.TIMELINE.value: "Timeline",
        RiskCategory.TECHNICAL.value: "Technical",
        RiskCategory.COMPLIANCE.value: "Compliance",
    }


def get_severity_display_names() -> dict[str, str]:
    """Get user-friendly severity names for UI."""
    return {
        RiskSeverity.CRITICAL.value: "Critical",
        RiskSeverity.HIGH.value: "High",
        RiskSeverity.MEDIUM.value: "Medium",
        RiskSeverity.LOW.value: "Low",
    }
