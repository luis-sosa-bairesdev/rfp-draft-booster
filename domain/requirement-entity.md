# Domain Entity: Requirement

## Overview

The Requirement entity represents individual requirements extracted from RFP documents using AI-powered extraction. These requirements are categorized, prioritized, and matched to internal service offerings.

---

## Attributes

### Core Identifiers

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | UUID | Yes | Unique identifier for the requirement |
| `rfp_id` | UUID | Yes | Foreign key to parent RFP |

### Content

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `description` | Text | Yes | Full requirement text extracted from RFP |
| `category` | Enum | Yes | Type: `technical`, `functional`, `timeline`, `budget`, `compliance` |
| `priority` | Enum | Yes | Importance: `critical`, `high`, `medium`, `low` |

### Source Information

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `page_number` | Integer | No | Source page in PDF (if available) |
| `section` | String | No | Section heading from RFP |
| `original_text` | Text | No | Raw text before processing |

### Quality Metrics

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `confidence_score` | Float | Yes | AI extraction confidence (0.0-1.0) |
| `extraction_method` | Enum | Yes | `llm`, `regex`, `manual` |
| `needs_review` | Boolean | Yes | Flagged for manual review if confidence < 0.7 |

### Verification

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `manually_verified` | Boolean | Yes | User has reviewed and approved |
| `verified_by` | String | No | Email of verifying user |
| `verified_date` | Timestamp | No | When verification occurred |
| `edited` | Boolean | Yes | User modified after extraction |

### Timestamps

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `extracted_date` | Timestamp | Yes | When requirement was extracted |
| `last_modified` | Timestamp | Yes | Last update timestamp |

---

## Enumerations

### Category Types

```python
class RequirementCategory(Enum):
    TECHNICAL = "technical"          # Technology, architecture, performance
    FUNCTIONAL = "functional"        # Features, capabilities, use cases
    TIMELINE = "timeline"            # Deadlines, milestones, phases
    BUDGET = "budget"               # Pricing, cost constraints
    COMPLIANCE = "compliance"       # Legal, regulatory, security
```

**Examples:**
- **Technical:** "Solution must support 99.9% uptime SLA"
- **Functional:** "System must generate reports in PDF and Excel"
- **Timeline:** "Implementation must complete within 90 days"
- **Budget:** "Total project cost not to exceed $500K"
- **Compliance:** "Must be HIPAA compliant"

### Priority Levels

```python
class RequirementPriority(Enum):
    CRITICAL = "critical"    # Must-have, deal-breaker
    HIGH = "high"           # Very important, strong preference
    MEDIUM = "medium"       # Important, but negotiable
    LOW = "low"            # Nice-to-have
```

### Extraction Methods

```python
class ExtractionMethod(Enum):
    LLM = "llm"         # Extracted via LLM (Gemini, Groq, etc.)
    REGEX = "regex"     # Pattern matching
    MANUAL = "manual"   # User-entered
```

---

## Business Rules

### Validation Rules

1. **Description Length:** Minimum 10 characters, maximum 5000 characters
2. **Confidence Score:** Must be between 0.0 and 1.0
3. **Category Required:** Must be one of the defined categories
4. **Priority Required:** Must be one of the defined priorities
5. **RFP Association:** Must be linked to a valid RFP

### Quality Thresholds

```python
HIGH_CONFIDENCE = 0.85   # Auto-approve
MEDIUM_CONFIDENCE = 0.70  # Manual review recommended
LOW_CONFIDENCE = 0.60    # Requires manual verification
```

### Review Rules

1. **Auto-Review Threshold:** Confidence ≥ 0.85 → No review needed
2. **Manual Review:** Confidence < 0.70 → `needs_review = True`
3. **Verification:** Users can verify any requirement
4. **Edit Tracking:** Any user edit sets `edited = True`

---

## Relationships

### Parent-Child

- **RFP (1) → Requirements (N):** One RFP has many Requirements

### Many-to-Many

- **Requirements (N) ↔ Services (M):** Via ServiceMatch entity

---

## Example Instances

### Technical Requirement

```json
{
  "id": "req-987f6543-e21b-45d3-b789-426614174111",
  "rfp_id": "rfp-123e4567-e89b-12d3-a456-426614174000",
  
  "description": "Solution must support 99.9% uptime SLA with automated failover capabilities and real-time monitoring",
  "category": "technical",
  "priority": "critical",
  
  "page_number": 12,
  "section": "Technical Requirements",
  "original_text": "The proposed solution shall maintain a minimum uptime of 99.9% with automated failover...",
  
  "confidence_score": 0.95,
  "extraction_method": "llm",
  "needs_review": false,
  
  "manually_verified": true,
  "verified_by": "john.doe@company.com",
  "verified_date": "2025-11-07T10:35:00Z",
  "edited": false,
  
  "extracted_date": "2025-11-07T10:30:45Z",
  "last_modified": "2025-11-07T10:35:00Z"
}
```

### Budget Requirement

```json
{
  "id": "req-456a7890-b12c-34d5-e678-426614174222",
  "rfp_id": "rfp-123e4567-e89b-12d3-a456-426614174000",
  
  "description": "Total project cost must not exceed $500,000 including all licensing, implementation, and training",
  "category": "budget",
  "priority": "high",
  
  "page_number": 8,
  "section": "Budget Constraints",
  "original_text": "Budget: Maximum $500K all-inclusive",
  
  "confidence_score": 0.68,
  "extraction_method": "llm",
  "needs_review": true,
  
  "manually_verified": false,
  "verified_by": null,
  "verified_date": null,
  "edited": false,
  
  "extracted_date": "2025-11-07T10:30:50Z",
  "last_modified": "2025-11-07T10:30:50Z"
}
```

---

## Common Queries

### Get all requirements for an RFP

```python
requirements = Requirement.filter(rfp_id="rfp-123e4567")
```

### Get high-priority requirements

```python
critical_reqs = Requirement.filter(
    rfp_id="rfp-123e4567",
    priority__in=["critical", "high"]
)
```

### Get requirements needing review

```python
needs_review = Requirement.filter(
    rfp_id="rfp-123e4567",
    needs_review=True
)
```

### Get technical requirements

```python
technical = Requirement.filter(
    rfp_id="rfp-123e4567",
    category="technical"
)
```

---

## Usage in Code

### Python Model

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum

class RequirementCategory(Enum):
    TECHNICAL = "technical"
    FUNCTIONAL = "functional"
    TIMELINE = "timeline"
    BUDGET = "budget"
    COMPLIANCE = "compliance"

class RequirementPriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class ExtractionMethod(Enum):
    LLM = "llm"
    REGEX = "regex"
    MANUAL = "manual"

@dataclass
class Requirement:
    id: str
    rfp_id: str
    
    description: str
    category: RequirementCategory
    priority: RequirementPriority
    
    page_number: Optional[int]
    section: Optional[str]
    original_text: Optional[str]
    
    confidence_score: float
    extraction_method: ExtractionMethod
    needs_review: bool
    
    manually_verified: bool
    verified_by: Optional[str]
    verified_date: Optional[datetime]
    edited: bool
    
    extracted_date: datetime
    last_modified: datetime
    
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
```

---

## Validation Examples

### Description Validation

```python
def validate_description(description: str) -> None:
    if len(description) < 10:
        raise ValueError("Description must be at least 10 characters")
    if len(description) > 5000:
        raise ValueError("Description exceeds 5000 character limit")
```

### Confidence Score Validation

```python
def validate_confidence(score: float) -> None:
    if not 0.0 <= score <= 1.0:
        raise ValueError(f"Confidence score {score} must be between 0.0 and 1.0")
```

### Auto-Review Flag

```python
def set_review_flag(confidence: float) -> bool:
    """Determine if requirement needs manual review."""
    return confidence < 0.70
```

---

## Related Entities

- **[RFP Entity](rfp-entity.md)** - Parent RFP document
- **[Service Entity](service-catalog-entity.md)** - Services matched to requirements
- **[ServiceMatch Entity](service-catalog-entity.md#servicematch)** - Matching relationships

---

## Notes

- Requirements are mutable (users can edit description, category, priority)
- Editing sets `edited = True` and updates `last_modified`
- Confidence score is immutable after extraction
- Low-confidence requirements should be reviewed before draft generation
- Requirements drive service matching algorithm
- Critical and high-priority requirements weighted higher in matching

