"""
Mock data generators for testing and fallback scenarios.

This module provides mock data generators for:
- Requirements
- Risks
- Drafts
- RFPs

Used when:
- LLM API fails or returns empty results
- Testing/demo mode
- Offline development
"""

import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)


# ============================================================================
# Mock Requirements
# ============================================================================

MOCK_REQUIREMENTS = [
    {
        "id": "req-demo-1",
        "description": "Cloud infrastructure with 99.9% uptime SLA and auto-scaling capabilities",
        "category": "Technical",
        "priority": "Critical",
        "confidence": 0.95,
        "page_number": 1,
        "verified": False,
        "source": "AI"
    },
    {
        "id": "req-demo-2",
        "description": "Multi-factor authentication for all user accounts with role-based access control",
        "category": "Technical",
        "priority": "High",
        "confidence": 0.92,
        "page_number": 2,
        "verified": False,
        "source": "AI"
    },
    {
        "id": "req-demo-3",
        "description": "Project completion within 6 months including UAT and deployment",
        "category": "Timeline",
        "priority": "Critical",
        "confidence": 0.88,
        "page_number": 3,
        "verified": False,
        "source": "AI"
    },
    {
        "id": "req-demo-4",
        "description": "Total project budget not to exceed $500,000 including all phases",
        "category": "Budget",
        "priority": "Critical",
        "confidence": 0.96,
        "page_number": 1,
        "verified": False,
        "source": "AI"
    },
    {
        "id": "req-demo-5",
        "description": "GDPR and SOC 2 Type II compliance for all data processing activities",
        "category": "Compliance",
        "priority": "High",
        "confidence": 0.94,
        "page_number": 4,
        "verified": False,
        "source": "AI"
    },
    {
        "id": "req-demo-6",
        "description": "RESTful API with OpenAPI documentation and versioning support",
        "category": "Functional",
        "priority": "High",
        "confidence": 0.90,
        "page_number": 5,
        "verified": False,
        "source": "AI"
    },
    {
        "id": "req-demo-7",
        "description": "Mobile responsive web application compatible with iOS and Android",
        "category": "Functional",
        "priority": "Medium",
        "confidence": 0.87,
        "page_number": 6,
        "verified": False,
        "source": "AI"
    },
    {
        "id": "req-demo-8",
        "description": "Automated backup and disaster recovery with RPO of 1 hour",
        "category": "Technical",
        "priority": "High",
        "confidence": 0.91,
        "page_number": 7,
        "verified": False,
        "source": "AI"
    }
]


# ============================================================================
# Mock Risks
# ============================================================================

MOCK_RISKS = [
    {
        "id": "risk-demo-1",
        "clause_text": "Vendor shall assume unlimited liability for any data breaches or security incidents",
        "category": "Legal",
        "severity": "Critical",
        "confidence": 0.93,
        "page_number": 2,
        "recommendation": "Negotiate a cap on liability based on contract value",
        "alternative_language": "Vendor's liability for data breaches shall be limited to [X] times the annual contract value",
        "acknowledged": False
    },
    {
        "id": "risk-demo-2",
        "clause_text": "All intellectual property rights shall transfer to the client upon project initiation",
        "category": "Legal",
        "severity": "High",
        "confidence": 0.89,
        "page_number": 8,
        "recommendation": "Request transfer only upon final delivery and full payment",
        "alternative_language": "Intellectual property rights shall transfer upon project completion and receipt of final payment",
        "acknowledged": False
    },
    {
        "id": "risk-demo-3",
        "clause_text": "Penalties of $10,000 per day for any delays beyond the initial deadline",
        "category": "Financial",
        "severity": "Critical",
        "confidence": 0.95,
        "page_number": 3,
        "recommendation": "Negotiate a grace period and lower penalties for early-stage delays",
        "alternative_language": "Penalties shall be $2,500 per week after a 2-week grace period",
        "acknowledged": False
    },
    {
        "id": "risk-demo-4",
        "clause_text": "Fixed-price contract with no allowance for scope changes or additional work",
        "category": "Financial",
        "severity": "High",
        "confidence": 0.91,
        "page_number": 9,
        "recommendation": "Include a change request process with time and materials pricing",
        "alternative_language": "Fixed price for defined scope; additional work billed at agreed hourly rates",
        "acknowledged": False
    },
    {
        "id": "risk-demo-5",
        "clause_text": "Project must achieve 100% feature completion with zero critical bugs at launch",
        "category": "Technical",
        "severity": "High",
        "confidence": 0.88,
        "page_number": 10,
        "recommendation": "Define 'critical bugs' clearly and allow for post-launch fixes",
        "alternative_language": "Project deemed complete when 95% of features work with no critical bugs blocking core functionality",
        "acknowledged": False
    }
]


# ============================================================================
# Mock Draft
# ============================================================================

MOCK_DRAFT_CONTENT = """# RFP Response - Cloud Infrastructure Modernization

## Executive Summary
We are pleased to submit our proposal for your cloud infrastructure modernization project. Our team has extensive experience delivering enterprise-grade cloud solutions with a focus on security, scalability, and compliance.

## Technical Approach

### Architecture Overview
Our proposed architecture leverages modern cloud-native technologies:
- **Infrastructure**: AWS with multi-AZ deployment
- **Container Orchestration**: Kubernetes (EKS)
- **CI/CD**: GitLab CI with automated testing
- **Monitoring**: Prometheus + Grafana stack

### Security & Compliance
- Multi-factor authentication (MFA) for all accounts
- Role-based access control (RBAC)
- Encryption at rest and in transit
- GDPR and SOC 2 Type II compliance

## Project Timeline
- **Phase 1** (Months 1-2): Infrastructure setup and migration
- **Phase 2** (Months 3-4): Application deployment and testing
- **Phase 3** (Months 5-6): UAT and production launch

## Budget
Total project cost: $485,000
- Infrastructure: $150,000
- Development: $220,000
- Testing & QA: $65,000
- Project Management: $50,000

## Team Qualifications
Our team brings over 50 years of combined experience in cloud infrastructure and has successfully delivered 30+ similar projects.

## Risk Mitigation
We have identified and addressed all key risks in your RFP, proposing alternative language where necessary to ensure project success.
"""


# ============================================================================
# Generator Functions
# ============================================================================

def generate_mock_requirements(
    count: int = None,
    seed: int = None
) -> List[Dict[str, Any]]:
    """
    Generate mock requirements.
    
    Args:
        count: Number of requirements to generate (None = all)
        seed: Random seed for reproducibility
    
    Returns:
        List of requirement dictionaries
    """
    if seed is not None:
        random.seed(seed)
    
    if count is None:
        requirements = MOCK_REQUIREMENTS.copy()
    else:
        # If count > len(MOCK_REQUIREMENTS), cycle through them
        requirements = []
        for i in range(count):
            req = MOCK_REQUIREMENTS[i % len(MOCK_REQUIREMENTS)].copy()
            req["id"] = f"req-demo-{i+1}"
            requirements.append(req)
    
    logger.info(f"Generated {len(requirements)} mock requirements")
    return requirements


def generate_mock_risks(
    count: int = None,
    seed: int = None
) -> List[Dict[str, Any]]:
    """
    Generate mock risks.
    
    Args:
        count: Number of risks to generate (None = all)
        seed: Random seed for reproducibility
    
    Returns:
        List of risk dictionaries
    """
    if seed is not None:
        random.seed(seed)
    
    if count is None:
        risks = MOCK_RISKS.copy()
    else:
        # If count > len(MOCK_RISKS), cycle through them
        risks = []
        for i in range(count):
            risk = MOCK_RISKS[i % len(MOCK_RISKS)].copy()
            risk["id"] = f"risk-demo-{i+1}"
            risks.append(risk)
    
    logger.info(f"Generated {len(risks)} mock risks")
    return risks


def generate_mock_draft(rfp_id: str = "demo-rfp") -> Dict[str, Any]:
    """
    Generate a mock draft.
    
    Args:
        rfp_id: ID of the RFP this draft is for
    
    Returns:
        Draft dictionary
    """
    draft = {
        "id": f"draft-{rfp_id}",
        "rfp_id": rfp_id,
        "content": MOCK_DRAFT_CONTENT,
        "status": "Draft",
        "generated_by": "AI",
        "word_count": len(MOCK_DRAFT_CONTENT.split()),
        "section_count": MOCK_DRAFT_CONTENT.count("##"),
        "completeness_score": 0.85
    }
    
    logger.info(f"Generated mock draft for RFP {rfp_id}")
    return draft


def generate_mock_rfp(
    file_name: str = "demo-rfp.pdf",
    client_name: str = "Demo Client Corp"
) -> Dict[str, Any]:
    """
    Generate a mock RFP.
    
    Args:
        file_name: Name of the RFP file
        client_name: Name of the client
    
    Returns:
        RFP dictionary
    """
    rfp = {
        "id": "demo-rfp-1",
        "file_name": file_name,
        "client_name": client_name,
        "extracted_text": "This is a sample RFP for cloud infrastructure modernization...",
        "page_count": 15,
        "deadline": (datetime.now() + timedelta(days=30)).isoformat(),
        "upload_date": datetime.now().isoformat()
    }
    
    logger.info(f"Generated mock RFP: {file_name} for {client_name}")
    return rfp


def is_mock_data_enabled() -> bool:
    """
    Check if mock data mode is enabled in session state.
    
    Returns:
        True if mock data should be used
    """
    try:
        import streamlit as st
        return st.session_state.get("use_mock_data", False)
    except ImportError:
        return False

