"""Requirement data model."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4


class RequirementCategory(Enum):
    """Requirement category types."""
    TECHNICAL = "technical"
    FUNCTIONAL = "functional"
    TIMELINE = "timeline"
    BUDGET = "budget"
    COMPLIANCE = "compliance"


class RequirementPriority(Enum):
    """Requirement priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ExtractionMethod(Enum):
    """How requirement was extracted."""
    LLM = "llm"
    REGEX = "regex"
    MANUAL = "manual"


@dataclass
class Requirement:
    """Individual requirement extracted from RFP."""
    
    # Core identifiers
    id: str = field(default_factory=lambda: f"req-{uuid4()}")
    rfp_id: str = ""
    
    # Content
    description: str = ""
    category: RequirementCategory = RequirementCategory.FUNCTIONAL
    priority: RequirementPriority = RequirementPriority.MEDIUM
    
    # Source information
    page_number: Optional[int] = None
    section: Optional[str] = None
    original_text: Optional[str] = None
    
    # Quality metrics
    confidence_score: float = 1.0
    extraction_method: ExtractionMethod = ExtractionMethod.MANUAL
    needs_review: bool = False
    
    # Verification
    manually_verified: bool = False
    verified_by: Optional[str] = None
    verified_date: Optional[datetime] = None
    edited: bool = False
    
    # Timestamps
    extracted_date: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)
    
    def is_high_confidence(self) -> bool:
        """Check if confidence score is high."""
        return self.confidence_score >= 0.85
    
    def requires_verification(self) -> bool:
        """Check if manual verification required."""
        return self.confidence_score < 0.70 or self.needs_review
    
    def mark_verified(self, user_email: str) -> None:
        """Mark requirement as verified by user."""
        self.manually_verified = True
        self.verified_by = user_email
        self.verified_date = datetime.now()
        self.needs_review = False
        self.last_modified = datetime.now()
    
    def update_content(self, new_description: str) -> None:
        """Update requirement description and mark as edited."""
        self.description = new_description
        self.edited = True
        self.last_modified = datetime.now()

