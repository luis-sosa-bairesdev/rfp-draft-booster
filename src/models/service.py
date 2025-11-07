"""Service and ServiceMatch data models."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import uuid4


class ServiceCategory(Enum):
    """Service category types."""
    CLOUD = "cloud"
    CONSULTING = "consulting"
    DEVELOPMENT = "development"
    SUPPORT = "support"
    INTEGRATION = "integration"
    TRAINING = "training"


class PricingModel(Enum):
    """Pricing model types."""
    FIXED = "fixed"
    HOURLY = "hourly"
    SUBSCRIPTION = "subscription"
    CUSTOM = "custom"


@dataclass
class Service:
    """Internal service offering."""
    
    # Core identifiers
    id: str = field(default_factory=lambda: f"svc-{uuid4()}")
    name: str = ""
    code: Optional[str] = None
    
    # Classification
    category: ServiceCategory = ServiceCategory.CONSULTING
    subcategory: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    # Description
    description: str = ""
    capabilities: List[str] = field(default_factory=list)
    key_benefits: Optional[List[str]] = None
    
    # Delivery
    typical_duration: Optional[str] = None
    team_size: Optional[str] = None
    delivery_model: Optional[str] = None
    
    # Pricing
    pricing_model: PricingModel = PricingModel.CUSTOM
    base_price: Optional[float] = None
    currency: Optional[str] = "USD"
    
    # Performance
    past_projects: int = 0
    success_rate: float = 0.0
    average_rating: Optional[float] = None
    
    # Status
    active: bool = True
    created_date: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def is_high_performer(self) -> bool:
        """Check if service has strong track record."""
        return self.success_rate >= 0.90 and self.past_projects >= 10


class MatchStatus(Enum):
    """Service match status."""
    SUGGESTED = "suggested"
    APPROVED = "approved"
    REJECTED = "rejected"
    ALTERNATIVE_NEEDED = "alternative_needed"


@dataclass
class ServiceMatch:
    """Requirement-to-service match."""
    
    # Core identifiers
    id: str = field(default_factory=lambda: f"match-{uuid4()}")
    requirement_id: str = ""
    service_id: str = ""
    
    # Match quality
    match_score: float = 0.0
    match_type: str = "medium"  # exact, high, medium, low
    reasoning: str = ""
    
    # Decision
    status: MatchStatus = MatchStatus.SUGGESTED
    suggested_date: datetime = field(default_factory=datetime.now)
    decision_date: Optional[datetime] = None
    approved_by: Optional[str] = None
    
    # Notes
    notes: Optional[str] = None
    alternative_service_id: Optional[str] = None
    
    def is_auto_approved(self) -> bool:
        """Check if match score is high enough for auto-approval."""
        return self.match_score >= 0.85
    
    def needs_review(self) -> bool:
        """Check if manual review needed."""
        return 0.70 <= self.match_score < 0.85
    
    def approve(self, user_email: str) -> None:
        """Approve the match."""
        self.status = MatchStatus.APPROVED
        self.approved_by = user_email
        self.decision_date = datetime.now()
    
    def reject(self, user_email: str, reason: Optional[str] = None) -> None:
        """Reject the match."""
        self.status = MatchStatus.REJECTED
        self.approved_by = user_email
        self.decision_date = datetime.now()
        if reason:
            self.notes = reason

