# Domain Entity: Draft

## Overview

The Draft entity represents generated proposal responses to RFPs. Drafts are created by combining AI-generated content with approved service matches and risk mitigations, then refined by users before export to Google Docs.

---

## Attributes

### Core Identifiers

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | UUID | Yes | Unique identifier for the draft |
| `rfp_id` | UUID | Yes | Foreign key to parent RFP |
| `version` | Integer | Yes | Version number (1, 2, 3...) |

### Content

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `content` | Text | Yes | Full draft text in Markdown format |
| `sections` | JSON | Yes | Structured sections with metadata |
| `title` | String | Yes | Draft title (usually RFP title) |

### Generation

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `generated_by` | Enum | Yes | `ai`, `hybrid`, `manual` |
| `llm_provider` | String | No | Which LLM used (gemini, groq, ollama) |
| `generation_time` | Float | No | Time taken to generate (seconds) |
| `generated_date` | Timestamp | Yes | When draft was created |

### Status

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `status` | Enum | Yes | `generated`, `editing`, `reviewed`, `approved`, `exported` |
| `editing_mode` | Boolean | Yes | Currently being edited |
| `locked_by` | String | No | User currently editing (for collaboration) |

### Metrics

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `word_count` | Integer | Yes | Total words in draft |
| `section_count` | Integer | Yes | Number of sections |
| `editing_time` | Integer | No | Total time spent editing (seconds) |
| `revision_count` | Integer | Yes | Number of times regenerated |

### Export

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `exported` | Boolean | Yes | Has been exported |
| `exported_to_gdocs` | Boolean | Yes | Exported to Google Docs |
| `gdocs_url` | String | No | Google Docs link |
| `export_date` | Timestamp | No | When exported |
| `exported_by` | String | No | User who exported |

### Approval

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `approved` | Boolean | Yes | Draft approved for submission |
| `approved_by` | String | No | Manager/user who approved |
| `approval_date` | Timestamp | No | When approved |
| `approval_notes` | Text | No | Approval comments |

### Quality Scores

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `completeness_score` | Float | No | How complete is draft (0.0-1.0) |
| `requirement_coverage` | Float | No | % of requirements addressed |
| `risk_coverage` | Float | No | % of risks addressed |

### Timestamps

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `created_date` | Timestamp | Yes | When draft record created |
| `last_modified` | Timestamp | Yes | Last update timestamp |

---

## Enumerations

### Draft Status

```python
class DraftStatus(Enum):
    GENERATED = "generated"    # AI generated, not yet edited
    EDITING = "editing"        # User is actively editing
    REVIEWED = "reviewed"      # User marked ready for review
    APPROVED = "approved"      # Manager/user approved
    EXPORTED = "exported"      # Exported to Google Docs
```

**Status Workflow:**

```
generated → editing → reviewed → approved → exported
    ↑         ↓
    └─────────┘ (can cycle between generated/editing)
```

### Generation Method

```python
class GenerationMethod(Enum):
    AI = "ai"           # Fully AI-generated
    HYBRID = "hybrid"   # AI + manual edits
    MANUAL = "manual"   # Manually written from scratch
```

---

## Section Structure

### Default Sections

```python
DEFAULT_SECTIONS = [
    "executive_summary",      # High-level overview
    "understanding",          # Our understanding of requirements
    "approach",              # Proposed methodology
    "services",              # Matched services and offerings
    "timeline",              # Project schedule and milestones
    "team",                  # Team composition
    "pricing",               # Cost breakdown
    "risk_mitigation",       # How we address identified risks
    "differentiators",       # Why choose us
    "case_studies",          # Relevant past projects
    "terms",                 # Terms and conditions
    "appendix"              # Supporting documents
]
```

### Section Metadata

```json
{
  "id": "exec_summary_001",
  "section_type": "executive_summary",
  "title": "Executive Summary",
  "content": "# Executive Summary\n\nACME Corporation seeks...",
  "word_count": 287,
  "order": 1,
  "generated_by": "ai",
  "user_edited": false,
  "status": "complete"
}
```

---

## Business Rules

### Generation Rules

1. **Minimum Word Count:** Draft must be at least 500 words
2. **Maximum Word Count:** Draft should not exceed 10,000 words
3. **Required Sections:** Executive summary, services, pricing minimum
4. **Risk Acknowledgment:** Critical risks must be acknowledged before generation
5. **Service Matches:** At least one approved service match required

### Version Control

1. **Auto-Increment:** Version number increments with each regeneration
2. **Version History:** Keep previous versions for 30 days
3. **Major Changes:** +1 version if >30% content changed
4. **Minor Edits:** Same version, track editing time

### Export Rules

1. **Status Check:** Can only export if status is `reviewed` or `approved`
2. **Completeness:** All required sections must be present
3. **Quality Gate:** `completeness_score` must be >= 0.80
4. **Google Docs:** Export creates new doc or updates existing

### Approval Rules

1. **Self-Approval:** Sales reps can approve own drafts if < $100K
2. **Manager Approval:** Required for proposals > $100K
3. **Legal Review:** Required if legal risks present
4. **Approval Cascade:** Lower status cannot approve higher (rep can't approve manager-required)

---

## Example Instance

```json
{
  "id": "draft-789d0123-e67f-89g0-h123-426614174555",
  "rfp_id": "rfp-123e4567-e89b-12d3-a456-426614174000",
  "version": 2,
  
  "content": "# Proposal for ACME Corp Cloud Migration\n\n## Executive Summary\n\nACME Corporation seeks...",
  "sections": [
    {
      "id": "exec_summary",
      "title": "Executive Summary",
      "order": 1,
      "word_count": 287,
      "user_edited": true
    },
    {
      "id": "approach",
      "title": "Our Approach",
      "order": 2,
      "word_count": 654,
      "user_edited": false
    }
  ],
  "title": "Cloud Infrastructure Migration Proposal - ACME Corp",
  
  "generated_by": "hybrid",
  "llm_provider": "gemini",
  "generation_time": 45.2,
  "generated_date": "2025-11-07T10:32:00Z",
  
  "status": "approved",
  "editing_mode": false,
  "locked_by": null,
  
  "word_count": 3250,
  "section_count": 10,
  "editing_time": 1847,
  "revision_count": 1,
  
  "exported": true,
  "exported_to_gdocs": true,
  "gdocs_url": "https://docs.google.com/document/d/abc123xyz789/edit",
  "export_date": "2025-11-07T15:30:00Z",
  "exported_by": "john.doe@company.com",
  
  "approved": true,
  "approved_by": "manager@company.com",
  "approval_date": "2025-11-07T15:45:00Z",
  "approval_notes": "Excellent proposal. Make sure to emphasize our experience with similar projects in the presentation.",
  
  "completeness_score": 0.92,
  "requirement_coverage": 0.95,
  "risk_coverage": 1.0,
  
  "created_date": "2025-11-07T10:32:00Z",
  "last_modified": "2025-11-07T15:45:00Z"
}
```

---

## Common Queries

### Get latest draft for RFP

```python
latest_draft = Draft.filter(rfp_id="rfp-123e4567").order_by('-version').first()
```

### Get approved drafts

```python
approved = Draft.filter(approved=True, exported=False)
```

### Get drafts pending approval

```python
pending = Draft.filter(status="reviewed", approved=False)
```

### Get draft edit history

```python
versions = Draft.filter(rfp_id="rfp-123e4567").order_by('version')
```

---

## Usage in Code

### Python Model

```python
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum

class DraftStatus(Enum):
    GENERATED = "generated"
    EDITING = "editing"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    EXPORTED = "exported"

class GenerationMethod(Enum):
    AI = "ai"
    HYBRID = "hybrid"
    MANUAL = "manual"

@dataclass
class DraftSection:
    id: str
    section_type: str
    title: str
    content: str
    word_count: int
    order: int
    generated_by: str
    user_edited: bool
    status: str

@dataclass
class Draft:
    id: str
    rfp_id: str
    version: int
    
    content: str
    sections: List[DraftSection]
    title: str
    
    generated_by: GenerationMethod
    llm_provider: Optional[str]
    generation_time: Optional[float]
    generated_date: datetime
    
    status: DraftStatus
    editing_mode: bool
    locked_by: Optional[str]
    
    word_count: int
    section_count: int
    editing_time: Optional[int]
    revision_count: int
    
    exported: bool
    exported_to_gdocs: bool
    gdocs_url: Optional[str]
    export_date: Optional[datetime]
    exported_by: Optional[str]
    
    approved: bool
    approved_by: Optional[str]
    approval_date: Optional[datetime]
    approval_notes: Optional[str]
    
    completeness_score: Optional[float]
    requirement_coverage: Optional[float]
    risk_coverage: Optional[float]
    
    created_date: datetime
    last_modified: datetime
    
    def can_export(self) -> bool:
        """Check if draft is ready for export."""
        return (
            self.status in [DraftStatus.REVIEWED, DraftStatus.APPROVED]
            and self.completeness_score >= 0.80
            and self.word_count >= 500
        )
    
    def requires_manager_approval(self, proposal_value: float) -> bool:
        """Check if manager approval needed based on value."""
        return proposal_value > 100000
    
    def calculate_completeness(self) -> float:
        """Calculate draft completeness score."""
        required_sections = ["executive_summary", "services", "pricing"]
        present = sum(1 for s in self.sections if s.section_type in required_sections)
        return present / len(required_sections)
    
    def get_section_by_type(self, section_type: str) -> Optional[DraftSection]:
        """Get specific section by type."""
        return next((s for s in self.sections if s.section_type == section_type), None)
```

---

## Generation Process

### Draft Generation Workflow

```python
def generate_draft(rfp_id: str) -> Draft:
    """Generate draft from RFP, requirements, matches, and risks."""
    
    # 1. Validate prerequisites
    rfp = get_rfp(rfp_id)
    if rfp.status != "completed":
        raise ValueError("RFP not yet processed")
    
    # 2. Check critical risks acknowledged
    blocking_risks = get_blocking_risks(rfp_id)
    if blocking_risks:
        raise ValueError("Critical risks must be acknowledged")
    
    # 3. Get approved service matches
    matches = get_approved_matches(rfp_id)
    if not matches:
        raise ValueError("No approved service matches")
    
    # 4. Generate sections
    sections = []
    for section_type in DEFAULT_SECTIONS:
        content = generate_section(section_type, rfp, matches)
        sections.append(DraftSection(
            id=f"{section_type}_{uuid4()}",
            section_type=section_type,
            content=content,
            ...
        ))
    
    # 5. Combine into full draft
    full_content = "\n\n".join(s.content for s in sections)
    
    # 6. Calculate metrics
    word_count = len(full_content.split())
    completeness = calculate_completeness(sections)
    
    # 7. Create draft record
    draft = Draft(
        id=str(uuid4()),
        rfp_id=rfp_id,
        version=get_next_version(rfp_id),
        content=full_content,
        sections=sections,
        word_count=word_count,
        completeness_score=completeness,
        ...
    )
    
    return draft
```

---

## Related Entities

- **[RFP Entity](rfp-entity.md)** - Parent RFP document
- **[Requirement Entity](requirement-entity.md)** - Requirements addressed in draft
- **[ServiceMatch Entity](service-catalog-entity.md#servicematch)** - Services included in draft
- **[RiskClause Entity](risk-clause-entity.md)** - Risks mitigated in draft

---

## Notes

- Drafts are versioned - never delete, create new version
- Markdown format allows easy conversion to Google Docs, PDF, Word
- Sections can be reordered by user for customization
- AI-generated content should be reviewed before export
- Export to Google Docs enables collaborative editing
- Track time spent editing to measure productivity gains
- Completeness score helps ensure quality before submission

