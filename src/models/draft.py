"""Draft data model."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import uuid4


class DraftStatus(Enum):
    """Draft status."""
    GENERATED = "generated"
    EDITING = "editing"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    EXPORTED = "exported"


class GenerationMethod(Enum):
    """How draft was generated."""
    AI = "ai"
    HYBRID = "hybrid"
    MANUAL = "manual"


@dataclass
class DraftSection:
    """Individual section of draft."""
    id: str = field(default_factory=lambda: str(uuid4()))
    section_type: str = ""
    title: str = ""
    content: str = ""
    word_count: int = 0
    order: int = 0
    generated_by: str = "ai"
    user_edited: bool = False
    status: str = "complete"
    
    def to_dict(self) -> dict:
        """Convert section to dictionary for serialization."""
        return {
            "id": self.id,
            "section_type": self.section_type,
            "title": self.title,
            "content": self.content,
            "word_count": self.word_count,
            "order": self.order,
            "generated_by": self.generated_by,
            "user_edited": self.user_edited,
            "status": self.status,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "DraftSection":
        """Create section from dictionary."""
        return cls(**data)


@dataclass
class Draft:
    """Generated proposal draft."""
    
    # Core identifiers
    id: str = field(default_factory=lambda: f"draft-{uuid4()}")
    rfp_id: str = ""
    version: int = 1
    
    # Content
    content: str = ""
    sections: List[DraftSection] = field(default_factory=list)
    title: str = ""
    
    # Generation
    generated_by: GenerationMethod = GenerationMethod.AI
    llm_provider: Optional[str] = None
    generation_time: Optional[float] = None
    generated_date: datetime = field(default_factory=datetime.now)
    
    # Status
    status: DraftStatus = DraftStatus.GENERATED
    editing_mode: bool = False
    locked_by: Optional[str] = None
    
    # Metrics
    word_count: int = 0
    section_count: int = 0
    editing_time: Optional[int] = None
    revision_count: int = 0
    
    # Export
    exported: bool = False
    exported_to_gdocs: bool = False
    gdocs_url: Optional[str] = None
    export_date: Optional[datetime] = None
    exported_by: Optional[str] = None
    
    # Approval
    approved: bool = False
    approved_by: Optional[str] = None
    approval_date: Optional[datetime] = None
    approval_notes: Optional[str] = None
    
    # Quality scores
    completeness_score: Optional[float] = None
    requirement_coverage: Optional[float] = None
    risk_coverage: Optional[float] = None
    
    # Timestamps
    created_date: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)
    
    def can_export(self) -> bool:
        """Check if draft is ready for export."""
        return (
            self.status in [DraftStatus.REVIEWED, DraftStatus.APPROVED]
            and (self.completeness_score or 0) >= 0.80
            and self.word_count >= 500
        )
    
    def requires_manager_approval(self, proposal_value: float) -> bool:
        """Check if manager approval needed based on value."""
        return proposal_value > 100000
    
    def calculate_completeness(self) -> float:
        """Calculate draft completeness score."""
        required_sections = ["executive_summary", "services", "pricing"]
        if not self.sections:
            return 0.0
        present = sum(1 for s in self.sections if s.section_type in required_sections)
        return present / len(required_sections)
    
    def get_section_by_type(self, section_type: str) -> Optional[DraftSection]:
        """Get specific section by type."""
        return next((s for s in self.sections if s.section_type == section_type), None)
    
    def update_content(self, new_content: str) -> None:
        """Update draft content and mark as edited."""
        self.content = new_content
        self.word_count = len(new_content.split())
        self.last_modified = datetime.now()
        if self.generated_by == GenerationMethod.AI:
            self.generated_by = GenerationMethod.HYBRID
    
    def to_dict(self) -> dict:
        """Convert draft to dictionary for serialization."""
        return {
            "id": self.id,
            "rfp_id": self.rfp_id,
            "version": self.version,
            "content": self.content,
            "sections": [s.to_dict() for s in self.sections],
            "title": self.title,
            "generated_by": self.generated_by.value if hasattr(self.generated_by, 'value') else str(self.generated_by),
            "llm_provider": self.llm_provider,
            "generation_time": self.generation_time,
            "generated_date": self.generated_date.isoformat(),
            "status": self.status.value if hasattr(self.status, 'value') else str(self.status),
            "editing_mode": self.editing_mode,
            "word_count": self.word_count,
            "section_count": self.section_count,
            "completeness_score": self.completeness_score,
            "created_date": self.created_date.isoformat(),
            "last_modified": self.last_modified.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Draft":
        """Create draft from dictionary."""
        # Parse datetime fields
        for date_field in ["generated_date", "created_date", "last_modified", "export_date", "approval_date"]:
            if isinstance(data.get(date_field), str):
                data[date_field] = datetime.fromisoformat(data[date_field])
        
        # Parse sections
        if "sections" in data and isinstance(data["sections"], list):
            data["sections"] = [DraftSection.from_dict(s) if isinstance(s, dict) else s for s in data["sections"]]
        
        # Parse enums
        if isinstance(data.get("generated_by"), str):
            data["generated_by"] = GenerationMethod(data["generated_by"])
        if isinstance(data.get("status"), str):
            data["status"] = DraftStatus(data["status"])
        
        return cls(**data)

