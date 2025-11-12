"""
Requirement data model for RFP requirements.

This module defines the data structures for storing and managing extracted requirements
from RFPs, including categorization, prioritization, and confidence scoring.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


class RequirementCategory(str, Enum):
    """Categories for requirements extracted from RFPs."""
    
    TECHNICAL = "technical"
    FUNCTIONAL = "functional"
    TIMELINE = "timeline"
    BUDGET = "budget"
    COMPLIANCE = "compliance"


class RequirementPriority(str, Enum):
    """Priority levels for requirements."""
    
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Requirement:
    """
    Represents a single requirement extracted from an RFP.
    
    Attributes:
        id: Unique identifier for the requirement
        rfp_id: ID of the RFP this requirement belongs to
        description: Clear, complete description of the requirement
        category: Type of requirement (technical, functional, etc.)
        priority: Importance level (critical, high, medium, low)
        confidence: AI's confidence in this extraction (0.0-1.0)
        page_number: Source page number in the RFP (if available)
        verified: Whether a human has verified this requirement
        notes: Additional notes or comments from users
        created_at: Timestamp when requirement was extracted
        updated_at: Timestamp of last modification
    """
    
    # Core fields
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    rfp_id: str = ""
    description: str = ""
    
    # Classification
    category: RequirementCategory = RequirementCategory.FUNCTIONAL
    priority: RequirementPriority = RequirementPriority.MEDIUM
    
    # Metadata
    confidence: float = 0.0
    page_number: Optional[int] = None
    verified: bool = False
    notes: str = ""
    
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
        
        # Convert string category/priority to enum if needed
        if isinstance(self.category, str):
            self.category = RequirementCategory(self.category.lower())
        
        if isinstance(self.priority, str):
            self.priority = RequirementPriority(self.priority.lower())
    
    def to_dict(self) -> dict:
        """Convert requirement to dictionary for serialization."""
        return {
            "id": self.id,
            "rfp_id": self.rfp_id,
            "description": self.description,
            "category": self.category.value,
            "priority": self.priority.value,
            "confidence": self.confidence,
            "page_number": self.page_number,
            "verified": self.verified,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Requirement":
        """Create requirement from dictionary."""
        # Parse datetime fields
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if isinstance(data.get("updated_at"), str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        
        return cls(**data)
    
    def update(self, **kwargs) -> None:
        """Update requirement fields and timestamp."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
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
    
    def get_priority_color(self) -> str:
        """Get color code for priority (for UI)."""
        colors = {
            RequirementPriority.CRITICAL: "#FF4444",  # Red
            RequirementPriority.HIGH: "#FF8800",  # Orange
            RequirementPriority.MEDIUM: "#FFBB00",  # Yellow
            RequirementPriority.LOW: "#4CAF50",  # Green
        }
        return colors.get(self.priority, "#808080")
    
    def get_category_icon(self) -> str:
        """Get emoji icon for category (for UI)."""
        icons = {
            RequirementCategory.TECHNICAL: "⚙️",
            RequirementCategory.FUNCTIONAL: "🎯",
            RequirementCategory.TIMELINE: "📅",
            RequirementCategory.BUDGET: "💰",
            RequirementCategory.COMPLIANCE: "✅",
        }
        return icons.get(self.category, "📋")


def get_category_display_names() -> dict[str, str]:
    """Get user-friendly category names for UI."""
    return {
        RequirementCategory.TECHNICAL.value: "Technical",
        RequirementCategory.FUNCTIONAL.value: "Functional",
        RequirementCategory.TIMELINE.value: "Timeline",
        RequirementCategory.BUDGET.value: "Budget",
        RequirementCategory.COMPLIANCE.value: "Compliance",
    }


def get_priority_display_names() -> dict[str, str]:
    """Get user-friendly priority names for UI."""
    return {
        RequirementPriority.CRITICAL.value: "Critical",
        RequirementPriority.HIGH.value: "High",
        RequirementPriority.MEDIUM.value: "Medium",
        RequirementPriority.LOW.value: "Low",
    }
