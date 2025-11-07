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

