# Domain Entity: RFP (Request for Proposal)

## Overview

The RFP entity represents the central document uploaded by sales teams containing requirements from potential clients. It serves as the starting point for the entire RFP Draft Booster workflow.

---

## Attributes

### Core Identifiers

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | UUID | Yes | Unique identifier for the RFP |
| `title` | String | Yes | User-provided name for the RFP document |
| `file_name` | String | Yes | Original PDF filename |

### File Metadata

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_size` | Integer | Yes | Size in bytes |
| `file_path` | String | Yes | Storage path for uploaded file |
| `total_pages` | Integer | Yes | Number of pages in PDF |

### Client Information

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `client_name` | String | Yes | Name of requesting company |
| `client_industry` | String | No | Industry sector |
| `client_size` | String | No | Company size (small, medium, large, enterprise) |

### Timeline

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `upload_date` | Timestamp | Yes | When RFP was uploaded |
| `deadline` | Timestamp | Yes | RFP submission deadline |
| `processing_start` | Timestamp | No | When processing began |
| `processing_end` | Timestamp | No | When processing completed |
| `processing_time` | Float | No | Time taken to process (seconds) |

### Status & Processing

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `status` | Enum | Yes | Current state: `uploaded`, `processing`, `completed`, `error` |
| `error_message` | String | No | Error details if status is `error` |
| `extracted_text` | Text | No | Full text content extracted from PDF |

### User & Ownership

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `uploaded_by` | String | Yes | User email who uploaded |
| `assigned_to` | String | No | User responsible for response |
| `team` | String | No | Sales team or department |

---

## Status Workflow

```
uploaded → processing → completed
                     ↓
                   error
```

### Status Definitions

- **uploaded:** File received, awaiting processing
- **processing:** Text extraction and analysis in progress
- **completed:** All extraction and analysis complete
- **error:** Processing failed, requires manual intervention

### Status Transitions

| From | To | Trigger | Validation |
|------|-----|---------|------------|
| uploaded | processing | Processing starts | File valid and readable |
| processing | completed | Processing succeeds | Requirements extracted |
| processing | error | Processing fails | Error logged |
| error | processing | User retries | User initiated |

---

## Business Rules

### Validation Rules

1. **File Size:** Must be ≤ 50MB (52,428,800 bytes)
2. **File Format:** Must be PDF with extractable text
3. **Title Uniqueness:** Title must be unique per user
4. **Deadline:** Must be a future date
5. **Client Name:** Required, minimum 2 characters
6. **Processing Timeout:** Max 5 minutes per RFP

### Data Quality Rules

1. **Confidence Threshold:** Extracted data below 0.7 confidence flagged
2. **Minimum Requirements:** At least 1 requirement must be extracted
3. **Text Extraction:** PDF must yield at least 100 characters
4. **Page Limit:** Support PDFs up to 200 pages

### Relationships

1. **One RFP has many Requirements:** 1:N relationship
2. **One RFP has many RiskClauses:** 1:N relationship
3. **One RFP has many Drafts:** 1:N relationship (versions)
4. **One RFP belongs to one User:** N:1 relationship

---

## Example Instance

```json
{
  "id": "rfp-123e4567-e89b-12d3-a456-426614174000",
  "title": "Cloud Infrastructure Migration - ACME Corp",
  "file_name": "ACME_RFP_2025_Q1.pdf",
  "file_size": 2457600,
  "file_path": "data/uploads/2025/11/rfp-123e4567.pdf",
  "total_pages": 45,
  
  "client_name": "ACME Corporation",
  "client_industry": "Technology",
  "client_size": "enterprise",
  
  "upload_date": "2025-11-07T10:30:00Z",
  "deadline": "2025-11-30T23:59:59Z",
  "processing_start": "2025-11-07T10:30:05Z",
  "processing_end": "2025-11-07T10:30:33Z",
  "processing_time": 28.5,
  
  "status": "completed",
  "error_message": null,
  "extracted_text": "Request for Proposal: Cloud Infrastructure Migration...",
  
  "uploaded_by": "john.doe@company.com",
  "assigned_to": "jane.smith@company.com",
  "team": "Enterprise Sales"
}
```

---

## Common Queries

### Find all RFPs for a user

```sql
SELECT * FROM rfps WHERE uploaded_by = 'user@company.com'
```

### Find RFPs due soon

```sql
SELECT * FROM rfps 
WHERE deadline < CURRENT_DATE + INTERVAL '7 days'
AND status = 'completed'
ORDER BY deadline ASC
```

### Find failed RFPs

```sql
SELECT * FROM rfps 
WHERE status = 'error'
ORDER BY upload_date DESC
```

---

## Usage in Code

### Python Model

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from enum import Enum

class RFPStatus(Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class RFP:
    id: str
    title: str
    file_name: str
    file_size: int
    file_path: str
    total_pages: int
    
    client_name: str
    client_industry: Optional[str]
    client_size: Optional[str]
    
    upload_date: datetime
    deadline: datetime
    processing_start: Optional[datetime]
    processing_end: Optional[datetime]
    processing_time: Optional[float]
    
    status: RFPStatus
    error_message: Optional[str]
    extracted_text: Optional[str]
    
    uploaded_by: str
    assigned_to: Optional[str]
    team: Optional[str]
    
    def is_overdue(self) -> bool:
        """Check if RFP deadline has passed."""
        return datetime.now() > self.deadline
    
    def days_until_deadline(self) -> int:
        """Calculate days remaining until deadline."""
        delta = self.deadline - datetime.now()
        return delta.days
    
    def size_mb(self) -> float:
        """Get file size in megabytes."""
        return self.file_size / (1024 * 1024)
```

---

## Validation Examples

### File Size Validation

```python
MAX_FILE_SIZE = 52428800  # 50MB

def validate_file_size(file_size: int) -> None:
    if file_size > MAX_FILE_SIZE:
        raise ValueError(f"File size {file_size} exceeds maximum {MAX_FILE_SIZE}")
    if file_size == 0:
        raise ValueError("File is empty")
```

### Deadline Validation

```python
from datetime import datetime

def validate_deadline(deadline: datetime) -> None:
    if deadline <= datetime.now():
        raise ValueError("Deadline must be in the future")
```

### Title Uniqueness Validation

```python
def validate_title_uniqueness(title: str, user_email: str, existing_rfps: List[RFP]) -> None:
    user_titles = [rfp.title for rfp in existing_rfps if rfp.uploaded_by == user_email]
    if title in user_titles:
        raise ValueError(f"RFP title '{title}' already exists for this user")
```

---

## Related Entities

- **[Requirement Entity](requirement-entity.md)** - Requirements extracted from RFP
- **[RiskClause Entity](risk-clause-entity.md)** - Risks detected in RFP
- **[Draft Entity](draft-entity.md)** - Generated proposal drafts

---

## Notes

- RFPs are immutable after upload (cannot edit PDF content)
- Users can update metadata (title, client name, deadline)
- Processing can be retried if status is `error`
- Extracted text is cached to avoid reprocessing
- Soft delete recommended (flag as deleted, don't remove from DB)

