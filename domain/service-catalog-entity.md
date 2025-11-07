# Domain Entity: Service & ServiceMatch

## Overview

The Service entity represents internal company offerings that can fulfill RFP requirements. ServiceMatch represents the relationship between Requirements and Services, capturing match quality and reasoning.

---

## Service Entity

### Attributes

#### Core Identifiers

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | UUID | Yes | Unique identifier for the service |
| `name` | String | Yes | Service name |
| `code` | String | No | Internal service code/SKU |

#### Classification

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `category` | Enum | Yes | `cloud`, `consulting`, `development`, `support`, `integration`, `training` |
| `subcategory` | String | No | More specific classification |
| `tags` | List[String] | Yes | Keywords for matching (min 3) |

#### Description

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `description` | Text | Yes | Detailed service description |
| `capabilities` | List[String] | Yes | List of capabilities/features (min 3) |
| `key_benefits` | List[String] | No | Main benefits for clients |

#### Delivery

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `typical_duration` | String | No | Estimated delivery time (e.g., "12-16 weeks") |
| `team_size` | String | No | Typical team composition |
| `delivery_model` | Enum | No | `fixed_price`, `time_material`, `subscription`, `hybrid` |

#### Pricing

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `pricing_model` | Enum | Yes | `fixed`, `hourly`, `subscription`, `custom` |
| `base_price` | Float | No | Starting price (if applicable) |
| `currency` | String | No | Currency code (USD, EUR, etc.) |

#### Performance

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `past_projects` | Integer | Yes | Number of similar projects completed |
| `success_rate` | Float | Yes | Historical success percentage (0.0-1.0) |
| `average_rating` | Float | No | Client satisfaction rating (0.0-5.0) |

#### Status

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `active` | Boolean | Yes | Whether service is currently offered |
| `created_date` | Timestamp | Yes | When service was added to catalog |
| `last_updated` | Timestamp | Yes | Last modification date |

---

## ServiceMatch Entity

### Overview

Links Requirements to matched Services with confidence scoring and reasoning.

### Attributes

#### Core Identifiers

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | UUID | Yes | Unique identifier for the match |
| `requirement_id` | UUID | Yes | Foreign key to Requirement |
| `service_id` | UUID | Yes | Foreign key to Service |

#### Match Quality

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `match_score` | Float | Yes | Algorithm confidence (0.0-1.0) |
| `match_type` | Enum | Yes | `exact`, `high`, `medium`, `low` |
| `reasoning` | Text | Yes | Explanation of why matched |

#### Decision

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `status` | Enum | Yes | `suggested`, `approved`, `rejected`, `alternative_needed` |
| `suggested_date` | Timestamp | Yes | When match was suggested |
| `decision_date` | Timestamp | No | When decision was made |
| `approved_by` | String | No | User who approved/rejected |

#### Notes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `notes` | Text | No | User comments on the match |
| `alternative_service_id` | UUID | No | If rejected, suggested alternative |

---

## Enumerations

### Service Categories

```python
class ServiceCategory(Enum):
    CLOUD = "cloud"                    # Cloud infrastructure, migration, ops
    CONSULTING = "consulting"          # Advisory, strategy, assessment
    DEVELOPMENT = "development"        # Custom software development
    SUPPORT = "support"               # Managed services, maintenance
    INTEGRATION = "integration"       # System integration, APIs
    TRAINING = "training"             # Training and enablement
```

### Pricing Models

```python
class PricingModel(Enum):
    FIXED = "fixed"                   # Fixed-price project
    HOURLY = "hourly"                 # Hourly rate
    SUBSCRIPTION = "subscription"     # Recurring subscription
    CUSTOM = "custom"                 # Custom pricing per project
```

### Delivery Models

```python
class DeliveryModel(Enum):
    FIXED_PRICE = "fixed_price"       # Fixed scope and price
    TIME_MATERIAL = "time_material"   # Flexible scope, billed by time
    SUBSCRIPTION = "subscription"     # Ongoing service
    HYBRID = "hybrid"                 # Combination
```

### Match Types

```python
class MatchType(Enum):
    EXACT = "exact"      # Perfect match (0.85-1.0)
    HIGH = "high"        # Strong match (0.70-0.84)
    MEDIUM = "medium"    # Moderate match (0.60-0.69)
    LOW = "low"          # Weak match (< 0.60)
```

### Match Status

```python
class MatchStatus(Enum):
    SUGGESTED = "suggested"              # Algorithm suggested
    APPROVED = "approved"                # User approved
    REJECTED = "rejected"                # User rejected
    ALTERNATIVE_NEEDED = "alternative_needed"  # Need different service
```

---

## Business Rules

### Service Rules

1. **Capabilities Minimum:** At least 3 capabilities required
2. **Tags Minimum:** At least 3 tags for matching algorithm
3. **Success Rate:** Must be between 0.0 and 1.0
4. **Active Only:** Only active services appear in matching
5. **Performance Tracking:** `past_projects` incremented with each win

### Matching Rules

1. **Auto-Approve Threshold:** `match_score >= 0.85` → Auto-approve
2. **Manual Review:** `0.70 <= match_score < 0.85` → Needs review
3. **Low Match:** `match_score < 0.70` → Flag for alternative
4. **Reasoning Required:** All matches must have reasoning
5. **One Requirement, Multiple Services:** Allowed (alternatives)

### Match Score Calculation

```python
def calculate_match_score(requirement: Requirement, service: Service) -> float:
    """
    Weighted calculation:
    - Semantic similarity (embedding): 60%
    - Keyword overlap: 20%
    - Category alignment: 10%
    - Historical success rate: 10%
    """
    semantic_score = get_embedding_similarity(requirement, service) * 0.6
    keyword_score = calculate_keyword_overlap(requirement, service) * 0.2
    category_score = category_alignment(requirement, service) * 0.1
    success_score = service.success_rate * 0.1
    
    return min(semantic_score + keyword_score + category_score + success_score, 1.0)
```

---

## Example Instances

### Service Example

```json
{
  "id": "svc-456a7890-b12c-34d5-e678-426614174222",
  "name": "Cloud Infrastructure Migration",
  "code": "CLD-MIG-001",
  
  "category": "cloud",
  "subcategory": "Migration & Modernization",
  "tags": [
    "cloud", "migration", "infrastructure", "AWS", "Azure", "GCP",
    "high-availability", "disaster-recovery", "architecture", "DevOps"
  ],
  
  "description": "Comprehensive cloud migration service including assessment, planning, execution, and optimization. We migrate workloads to AWS, Azure, or GCP with minimal downtime and risk.",
  "capabilities": [
    "Multi-cloud migration (AWS, Azure, GCP)",
    "High availability architecture design",
    "Disaster recovery setup and testing",
    "24/7 monitoring and support",
    "Performance optimization and cost reduction",
    "Security and compliance implementation"
  ],
  "key_benefits": [
    "99.9%+ uptime SLA",
    "30-40% infrastructure cost reduction",
    "Zero-downtime migration",
    "Enterprise-grade security"
  ],
  
  "typical_duration": "12-16 weeks",
  "team_size": "3 cloud architects, 2 DevOps engineers, 1 project manager",
  "delivery_model": "hybrid",
  
  "pricing_model": "custom",
  "base_price": 250000.00,
  "currency": "USD",
  
  "past_projects": 47,
  "success_rate": 0.94,
  "average_rating": 4.8,
  
  "active": true,
  "created_date": "2023-01-15T00:00:00Z",
  "last_updated": "2025-10-20T14:30:00Z"
}
```

### ServiceMatch Example

```json
{
  "id": "match-321b6543-c45d-67e8-f901-426614174333",
  "requirement_id": "req-987f6543-e21b-45d3-b789-426614174111",
  "service_id": "svc-456a7890-b12c-34d5-e678-426614174222",
  
  "match_score": 0.92,
  "match_type": "exact",
  "reasoning": "Service provides 99.9% uptime SLA with automated failover (requirement: 99.9%), includes real-time monitoring, and has proven track record with 94% success rate across 47 similar projects.",
  
  "status": "approved",
  "suggested_date": "2025-11-07T10:31:00Z",
  "decision_date": "2025-11-07T11:15:00Z",
  "approved_by": "john.doe@company.com",
  
  "notes": "Perfect fit for ACME's requirements. Highlight our experience with similar enterprise migrations.",
  "alternative_service_id": null
}
```

---

## Common Queries

### Get active cloud services

```python
services = Service.filter(category="cloud", active=True)
```

### Get high-performing services

```python
top_services = Service.filter(
    success_rate__gte=0.90,
    past_projects__gte=10
).order_by('-success_rate')
```

### Get matches for requirement

```python
matches = ServiceMatch.filter(
    requirement_id="req-987f6543",
    status__in=["suggested", "approved"]
).order_by('-match_score')
```

### Get approved matches for RFP

```python
approved = ServiceMatch.filter(
    requirement__rfp_id="rfp-123e4567",
    status="approved"
)
```

---

## Usage in Code

### Python Models

```python
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from enum import Enum

class ServiceCategory(Enum):
    CLOUD = "cloud"
    CONSULTING = "consulting"
    DEVELOPMENT = "development"
    SUPPORT = "support"
    INTEGRATION = "integration"
    TRAINING = "training"

class PricingModel(Enum):
    FIXED = "fixed"
    HOURLY = "hourly"
    SUBSCRIPTION = "subscription"
    CUSTOM = "custom"

@dataclass
class Service:
    id: str
    name: str
    code: Optional[str]
    
    category: ServiceCategory
    subcategory: Optional[str]
    tags: List[str]
    
    description: str
    capabilities: List[str]
    key_benefits: Optional[List[str]]
    
    typical_duration: Optional[str]
    team_size: Optional[str]
    delivery_model: Optional[str]
    
    pricing_model: PricingModel
    base_price: Optional[float]
    currency: Optional[str]
    
    past_projects: int
    success_rate: float
    average_rating: Optional[float]
    
    active: bool
    created_date: datetime
    last_updated: datetime
    
    def is_high_performer(self) -> bool:
        """Check if service has strong track record."""
        return self.success_rate >= 0.90 and self.past_projects >= 10

class MatchStatus(Enum):
    SUGGESTED = "suggested"
    APPROVED = "approved"
    REJECTED = "rejected"
    ALTERNATIVE_NEEDED = "alternative_needed"

@dataclass
class ServiceMatch:
    id: str
    requirement_id: str
    service_id: str
    
    match_score: float
    match_type: str
    reasoning: str
    
    status: MatchStatus
    suggested_date: datetime
    decision_date: Optional[datetime]
    approved_by: Optional[str]
    
    notes: Optional[str]
    alternative_service_id: Optional[str]
    
    def is_auto_approved(self) -> bool:
        """Check if match score is high enough for auto-approval."""
        return self.match_score >= 0.85
    
    def needs_review(self) -> bool:
        """Check if manual review needed."""
        return 0.70 <= self.match_score < 0.85
```

---

## Related Entities

- **[Requirement Entity](requirement-entity.md)** - Requirements being matched
- **[Draft Entity](draft-entity.md)** - Uses approved matches for generation

---

## Notes

- Service catalog should be maintained by product/sales team
- Tags are critical for matching algorithm effectiveness
- Historical performance data improves over time
- Inactive services excluded from matching but retained for history
- Match reasoning helps users understand AI decisions
- Alternative services help when primary match rejected

