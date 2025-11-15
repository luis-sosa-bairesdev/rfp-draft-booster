"""Service model for service matching.

This module defines the Service data model and related enums for
matching BairesDev services to RFP requirements.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
import json
from pathlib import Path


class ServiceCategory(str, Enum):
    """Service category enum."""
    TECHNICAL = "technical"
    FUNCTIONAL = "functional"
    TIMELINE = "timeline"
    BUDGET = "budget"
    COMPLIANCE = "compliance"


@dataclass
class Service:
    """Service model for service catalog.
    
    Represents a BairesDev service offering that can be matched
    to RFP requirements.
    """
    id: str
    name: str
    category: ServiceCategory
    description: str
    capabilities: List[str]
    success_rate: float = 0.95  # Default 95% success rate
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate service data after initialization."""
        # Convert category string to enum if needed
        if isinstance(self.category, str):
            self.category = ServiceCategory(self.category)
        
        # Validate success rate
        if not 0.0 <= self.success_rate <= 1.0:
            raise ValueError(f"Success rate must be between 0.0 and 1.0, got {self.success_rate}")
        
        # Ensure capabilities and tags are lists
        if not isinstance(self.capabilities, list):
            self.capabilities = [self.capabilities] if self.capabilities else []
        if not isinstance(self.tags, list):
            self.tags = [self.tags] if self.tags else []
    
    def to_dict(self) -> dict:
        """Convert service to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category.value,
            "description": self.description,
            "capabilities": self.capabilities,
            "success_rate": self.success_rate,
            "tags": self.tags
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Service":
        """Create service from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            category=data["category"],
            description=data["description"],
            capabilities=data.get("capabilities", []),
            success_rate=data.get("success_rate", 0.95),
            tags=data.get("tags", [])
        )
    
    def get_full_text(self) -> str:
        """Get full text representation for matching.
        
        Combines name, description, capabilities, and tags into
        a single text string for TF-IDF vectorization.
        """
        text_parts = [
            self.name,
            self.description,
            " ".join(self.capabilities),
            " ".join(self.tags)
        ]
        return " ".join(filter(None, text_parts))


def load_services_from_json(file_path: str = "data/services.json") -> List[Service]:
    """Load services from JSON file.
    
    Args:
        file_path: Path to services JSON file
        
    Returns:
        List of Service objects
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If JSON is malformed
        ValueError: If service data is invalid
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Services file not found: {file_path}")
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Invalid JSON in {file_path}: {e.msg}",
            e.doc,
            e.pos
        )
    
    # Validate structure
    if not isinstance(data, dict):
        raise ValueError(f"Services JSON must be a dict, got {type(data)}")
    
    if "services" not in data:
        raise ValueError("Services JSON must have 'services' key")
    
    if not isinstance(data["services"], list):
        raise ValueError(f"'services' must be a list, got {type(data['services'])}")
    
    # Parse services
    services = []
    for i, service_data in enumerate(data["services"]):
        try:
            service = Service.from_dict(service_data)
            services.append(service)
        except Exception as e:
            raise ValueError(f"Error parsing service at index {i}: {e}")
    
    return services


def get_default_services() -> List[Service]:
    """Get default services if JSON file doesn't exist.
    
    Returns a minimal set of BairesDev services for fallback.
    """
    return [
        Service(
            id="cloud-infrastructure",
            name="Cloud Infrastructure & DevOps",
            category=ServiceCategory.TECHNICAL,
            description="Design and implement scalable cloud infrastructure with CI/CD pipelines",
            capabilities=[
                "AWS/Azure/GCP deployment",
                "Kubernetes orchestration",
                "Docker containerization",
                "CI/CD automation",
                "Infrastructure as Code"
            ],
            success_rate=0.96,
            tags=["cloud", "devops", "kubernetes", "docker", "aws", "azure"]
        ),
        Service(
            id="custom-software-development",
            name="Custom Software Development",
            category=ServiceCategory.FUNCTIONAL,
            description="End-to-end custom software development with agile methodology",
            capabilities=[
                "Full-stack development",
                "Backend API development",
                "Frontend web applications",
                "Mobile app development",
                "Legacy system modernization"
            ],
            success_rate=0.95,
            tags=["development", "agile", "full-stack", "api", "web", "mobile"]
        ),
        Service(
            id="qa-testing",
            name="QA & Testing Services",
            category=ServiceCategory.COMPLIANCE,
            description="Comprehensive quality assurance and testing services",
            capabilities=[
                "Automated testing",
                "Manual testing",
                "Performance testing",
                "Security testing",
                "Test automation frameworks"
            ],
            success_rate=0.94,
            tags=["qa", "testing", "automation", "quality", "security"]
        )
    ]
