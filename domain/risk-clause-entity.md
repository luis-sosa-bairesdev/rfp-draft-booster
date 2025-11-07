# Domain Entity: RiskClause

## Overview

The RiskClause entity represents potentially problematic clauses detected in RFP documents that could pose legal, financial, timeline, technical, or compliance risks. Early risk detection helps sales teams address concerns proactively in their proposals.

---

## Attributes

### Core Identifiers

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | UUID | Yes | Unique identifier for the risk |
| `rfp_id` | UUID | Yes | Foreign key to parent RFP |

### Classification

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `risk_type` | Enum | Yes | `legal`, `financial`, `timeline`, `technical`, `compliance` |
| `severity` | Enum | Yes | `critical`, `high`, `medium`, `low` |
| `sub_category` | String | No | More specific risk classification |

### Content

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `clause_text` | Text | Yes | Exact problematic text from RFP |
| `page_number` | Integer | No | Source page in PDF |
| `section` | String | No | Section heading from RFP |

### Analysis

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `risk_description` | Text | Yes | What makes this clause risky |
| `potential_impact` | Text | No | Consequences if not addressed |
| `recommendation` | Text | Yes | Suggested action or mitigation |
| `alternative_language` | Text | No | Proposed alternative clause wording |

### Detection

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `detected_by` | Enum | Yes | `regex`, `llm`, `manual` |
| `confidence_score` | Float | Yes | Detection confidence (0.0-1.0) |
| `detection_pattern` | String | No | Regex pattern or LLM prompt used |

### Status

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `acknowledged` | Boolean | Yes | User/manager has reviewed |
| `acknowledged_by` | String | No | Email of acknowledging user |
| `acknowledgment_date` | Timestamp | No | When acknowledged |
| `resolved` | Boolean | Yes | Risk has been addressed in draft |
| `resolution_notes` | Text | No | How risk was handled |

### Timestamps

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `flagged_date` | Timestamp | Yes | When risk was detected |
| `last_updated` | Timestamp | Yes | Last modification date |

---

## Enumerations

### Risk Types

```python
class RiskType(Enum):
    LEGAL = "legal"              # Legal liability, IP, warranties
    FINANCIAL = "financial"      # Payment terms, penalties, unlimited costs
    TIMELINE = "timeline"        # Unrealistic deadlines, dependencies
    TECHNICAL = "technical"      # Impossible requirements, tech debt
    COMPLIANCE = "compliance"    # Regulatory, certification requirements
```

**Examples by Type:**

**Legal Risks:**
- Unlimited liability clauses
- IP ownership transfers
- Indemnification without limits
- Non-compete restrictions

**Financial Risks:**
- Unlimited revisions
- Penalty clauses without caps
- Below-market pricing requirements
- Payment terms > 90 days

**Timeline Risks:**
- Impossibly short deadlines
- Dependent on third-party deliveries
- No buffer for approvals

**Technical Risks:**
- Unsupported technology requirements
- Performance guarantees beyond capability
- 100% uptime requirements

**Compliance Risks:**
- Certifications not yet obtained
- Regulatory requirements not met
- Data sovereignty conflicts

### Severity Levels

```python
class RiskSeverity(Enum):
    CRITICAL = "critical"    # Deal-breaker, blocks draft generation
    HIGH = "high"           # Significant concern, requires manager approval
    MEDIUM = "medium"       # Important to address, but manageable
    LOW = "low"            # Minor issue, note in proposal
```

**Severity Criteria:**

| Severity | Criteria | Action Required |
|----------|----------|-----------------|
| Critical | Legal liability, project failure risk | Block draft until acknowledged |
| High | Financial exposure > $100K, regulatory | Manager approval required |
| Medium | Potential delays, scope creep | Note in risk section |
| Low | Minor inconvenience, cosmetic | Optional mention |

### Detection Methods

```python
class DetectionMethod(Enum):
    REGEX = "regex"      # Pattern matching (keywords like "unlimited", "penalty")
    LLM = "llm"         # AI semantic analysis
    MANUAL = "manual"   # User-flagged
```

---

## Business Rules

### Detection Rules

1. **Confidence Threshold:** Confidence < 0.6 requires manual verification
2. **Critical Blocking:** Critical risks with `acknowledged=False` block draft generation
3. **Manager Escalation:** High-severity risks notify manager automatically
4. **Duplicate Prevention:** Same clause text on same page = duplicate (skip)

### Acknowledgment Rules

1. **Critical Risks:** Only manager can acknowledge critical risks
2. **Acknowledgment Required:** All risks severity >= high must be acknowledged
3. **Resolution Tracking:** Acknowledged ≠ Resolved (separate flags)
4. **Audit Trail:** All acknowledgments logged with user and timestamp

### Severity Auto-Assignment

```python
def auto_assign_severity(risk_type: str, keywords: List[str]) -> str:
    """Auto-assign severity based on keywords."""
    critical_keywords = ["unlimited", "uncapped", "sole liability", "no limit"]
    high_keywords = ["penalty", "liquidated damages", "forfeit", "indemnify"]
    
    if any(kw in keywords for kw in critical_keywords):
        return "critical"
    elif any(kw in keywords for kw in high_keywords):
        return "high"
    else:
        return "medium"
```

---

## Example Instances

### Financial Risk (Critical)

```json
{
  "id": "risk-654c9876-d56e-78f9-g012-426614174444",
  "rfp_id": "rfp-123e4567-e89b-12d3-a456-426614174000",
  
  "risk_type": "financial",
  "severity": "critical",
  "sub_category": "Unlimited Liability",
  
  "clause_text": "Vendor shall provide unlimited revisions at no additional cost until client is fully satisfied",
  "page_number": 23,
  "section": "Terms and Conditions",
  
  "risk_description": "Unlimited revisions clause creates unbounded cost liability and potential for project never closing",
  "potential_impact": "Project could exceed budget by 200-300% with no recourse. Historical data shows 'unlimited' clauses cost average $150K in scope creep.",
  "recommendation": "Propose maximum 3 revision rounds included in base price. Additional revisions at 50% of hourly rate. Define clear acceptance criteria.",
  "alternative_language": "Vendor shall provide up to three (3) rounds of revisions at no additional cost. Additional revisions will be billed at $150/hour.",
  
  "detected_by": "llm",
  "confidence_score": 0.88,
  "detection_pattern": null,
  
  "acknowledged": true,
  "acknowledged_by": "manager@company.com",
  "acknowledgment_date": "2025-11-07T11:30:00Z",
  "resolved": false,
  "resolution_notes": null,
  
  "flagged_date": "2025-11-07T10:31:15Z",
  "last_updated": "2025-11-07T11:30:00Z"
}
```

### Legal Risk (High)

```json
{
  "id": "risk-789a0123-f45g-67h8-i901-426614174555",
  "rfp_id": "rfp-123e4567-e89b-12d3-a456-426614174000",
  
  "risk_type": "legal",
  "severity": "high",
  "sub_category": "IP Ownership",
  
  "clause_text": "All intellectual property developed during the project, including any pre-existing tools or frameworks, becomes the exclusive property of the client",
  "page_number": 18,
  "section": "Intellectual Property Rights",
  
  "risk_description": "Clause requires transfer of pre-existing IP and proprietary tools, which is non-negotiable for our company",
  "potential_impact": "Cannot use our standard frameworks and accelerators on future projects. Loss of competitive advantage.",
  "recommendation": "Clarify that only IP created specifically for this project transfers. Pre-existing tools and frameworks remain our property with license granted to client.",
  "alternative_language": "All intellectual property developed specifically and solely for this project becomes client property. Vendor retains ownership of pre-existing tools, frameworks, and methodologies, with perpetual license granted to client for project use.",
  
  "detected_by": "llm",
  "confidence_score": 0.92,
  "detection_pattern": null,
  
  "acknowledged": true,
  "acknowledged_by": "legal@company.com",
  "acknowledgment_date": "2025-11-07T12:00:00Z",
  "resolved": true,
  "resolution_notes": "Addressed in Section 5 of draft proposal with alternative language",
  
  "flagged_date": "2025-11-07T10:31:20Z",
  "last_updated": "2025-11-07T14:15:00Z"
}
```

### Timeline Risk (Medium)

```json
{
  "id": "risk-012b3456-c78d-90e1-f234-426614174666",
  "rfp_id": "rfp-123e4567-e89b-12d3-a456-426614174000",
  
  "risk_type": "timeline",
  "severity": "medium",
  "sub_category": "Aggressive Deadline",
  
  "clause_text": "Project must be completed within 60 days from contract signing",
  "page_number": 9,
  "section": "Timeline Requirements",
  
  "risk_description": "60-day timeline for full cloud migration is aggressive. Industry standard is 12-16 weeks for similar scope.",
  "potential_impact": "Risk of quality issues, missed deadline, or need for additional resources (cost overrun).",
  "recommendation": "Propose phased approach: Phase 1 (MVP) in 60 days, Phase 2 (full migration) at 90 days. Highlight risk-benefit tradeoff of faster timeline.",
  "alternative_language": "Phase 1 delivery (core infrastructure) within 60 days. Phase 2 (full migration and optimization) within 90 days total. Faster delivery possible with additional resources at increased cost.",
  
  "detected_by": "regex",
  "confidence_score": 0.75,
  "detection_pattern": "\\d{1,2}\\s+days",
  
  "acknowledged": true,
  "acknowledged_by": "john.doe@company.com",
  "acknowledgment_date": "2025-11-07T11:45:00Z",
  "resolved": true,
  "resolution_notes": "Proposed phased timeline in draft with clear milestones",
  
  "flagged_date": "2025-11-07T10:31:25Z",
  "last_updated": "2025-11-07T14:20:00Z"
}
```

---

## Common Queries

### Get all critical risks for RFP

```python
critical_risks = RiskClause.filter(
    rfp_id="rfp-123e4567",
    severity="critical"
)
```

### Get unacknowledged high/critical risks

```python
pending_risks = RiskClause.filter(
    rfp_id="rfp-123e4567",
    severity__in=["critical", "high"],
    acknowledged=False
)
```

### Get legal risks

```python
legal_risks = RiskClause.filter(
    rfp_id="rfp-123e4567",
    risk_type="legal"
).order_by('-severity')
```

### Check if draft generation is blocked

```python
blocking_risks = RiskClause.filter(
    rfp_id="rfp-123e4567",
    severity="critical",
    acknowledged=False
).count()

can_generate_draft = blocking_risks == 0
```

---

## Usage in Code

### Python Model

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum

class RiskType(Enum):
    LEGAL = "legal"
    FINANCIAL = "financial"
    TIMELINE = "timeline"
    TECHNICAL = "technical"
    COMPLIANCE = "compliance"

class RiskSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class DetectionMethod(Enum):
    REGEX = "regex"
    LLM = "llm"
    MANUAL = "manual"

@dataclass
class RiskClause:
    id: str
    rfp_id: str
    
    risk_type: RiskType
    severity: RiskSeverity
    sub_category: Optional[str]
    
    clause_text: str
    page_number: Optional[int]
    section: Optional[str]
    
    risk_description: str
    potential_impact: Optional[str]
    recommendation: str
    alternative_language: Optional[str]
    
    detected_by: DetectionMethod
    confidence_score: float
    detection_pattern: Optional[str]
    
    acknowledged: bool
    acknowledged_by: Optional[str]
    acknowledgment_date: Optional[datetime]
    resolved: bool
    resolution_notes: Optional[str]
    
    flagged_date: datetime
    last_updated: datetime
    
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
```

---

## Detection Patterns

### Regex Patterns for Common Risks

```python
RISK_PATTERNS = {
    "unlimited_liability": r"\b(unlimited|uncapped|no\s+limit)\b.*\b(liability|responsibility|revisions)\b",
    "penalty_clause": r"\b(penalty|liquidated\s+damages|forfeit)\b",
    "aggressive_timeline": r"\b(\d{1,2})\s+days?\b",
    "payment_terms": r"\bpayment.*\b(\d{2,3})\s+days?\b",
    "ip_transfer": r"\b(all|any)\s+(intellectual\s+property|IP)\b.*\b(property\s+of|belongs\s+to)\b"
}
```

### LLM Prompt for Risk Detection

```python
RISK_DETECTION_PROMPT = """
Analyze the following RFP clause and identify any risks:

Clause: {clause_text}

Identify:
1. Risk Type (legal, financial, timeline, technical, compliance)
2. Severity (critical, high, medium, low)
3. Why it's risky
4. Potential business impact
5. Recommendation to address

Output as JSON.
"""
```

---

## Related Entities

- **[RFP Entity](rfp-entity.md)** - Parent RFP document
- **[Draft Entity](draft-entity.md)** - Draft includes risk mitigation section

---

## Notes

- Critical risks must be acknowledged before draft generation
- Risk detection improves with historical data and patterns
- Users can add manual risks if AI misses something
- Resolved ≠ risk eliminated, means addressed in proposal
- Track patterns of successful risk mitigation for future use
- Legal team should review high/critical legal risks

