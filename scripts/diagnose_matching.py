#!/usr/bin/env python3
"""Diagnostic script to understand why service matching is failing."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.service import load_services_from_json, get_default_services
from models import Requirement, RequirementCategory, RequirementPriority
from services.service_matcher import ServiceMatcher

def test_matching():
    """Test service matching with sample requirements."""
    
    print("=" * 80)
    print("SERVICE MATCHING DIAGNOSTIC TOOL")
    print("=" * 80)
    
    # Load services
    try:
        services = load_services_from_json("data/services.json")
        print(f"\n✅ Loaded {len(services)} services from data/services.json")
    except Exception as e:
        print(f"\n❌ Error loading services: {e}")
        services = get_default_services()
        print(f"   Using {len(services)} default services")
    
    # Print service info
    print("\n📋 Available Services:")
    for i, service in enumerate(services, 1):
        print(f"\n{i}. {service.name} ({service.category.value})")
        print(f"   Description: {service.description[:100]}...")
        print(f"   Capabilities: {len(service.capabilities)} items")
        print(f"   Tags: {', '.join(service.tags[:5])}" + ("..." if len(service.tags) > 5 else ""))
        full_text = service.get_full_text()
        print(f"   Full text length: {len(full_text)} chars")
        print(f"   Sample keywords: {' '.join(full_text.split()[:10])}...")
    
    # Initialize matcher
    print("\n" + "=" * 80)
    print("INITIALIZING MATCHER")
    print("=" * 80)
    matcher = ServiceMatcher(services)
    print(f"✅ Matcher initialized")
    print(f"   Vocabulary size: {len(matcher.vectorizer.vocabulary_) if matcher.vectorizer else 0}")
    
    # Test with different requirement styles
    test_requirements = [
        # Style 1: Detailed (like AI extraction)
        Requirement(
            id="test-1",
            rfp_id="test",
            description="The system must be deployed on AWS cloud infrastructure with multi-region support for high availability and disaster recovery. Implementation should include Kubernetes orchestration for container management with automated scaling policies, and CI/CD pipelines using GitHub Actions or Jenkins for continuous integration and deployment. Infrastructure as Code with Terraform is required for reproducible infrastructure provisioning.",
            category=RequirementCategory.TECHNICAL,
            priority=RequirementPriority.CRITICAL,
            confidence=0.98
        ),
        # Style 2: Concise with keywords
        Requirement(
            id="test-2",
            rfp_id="test",
            description="AWS Kubernetes Docker CI/CD Terraform infrastructure deployment",
            category=RequirementCategory.TECHNICAL,
            priority=RequirementPriority.CRITICAL,
            confidence=0.98
        ),
        # Style 3: Mixed
        Requirement(
            id="test-3",
            rfp_id="test",
            description="Need cloud deployment using AWS, Kubernetes orchestration, and CI/CD pipelines",
            category=RequirementCategory.TECHNICAL,
            priority=RequirementPriority.HIGH,
            confidence=0.95
        ),
        # Style 4: QA Testing
        Requirement(
            id="test-4",
            rfp_id="test",
            description="Automated testing using Selenium and Cypress with continuous test execution. Performance and load testing to handle 10,000 concurrent users. Security testing following OWASP guidelines.",
            category=RequirementCategory.COMPLIANCE,
            priority=RequirementPriority.HIGH,
            confidence=0.97
        ),
    ]
    
    print("\n" + "=" * 80)
    print("TESTING DIFFERENT REQUIREMENT STYLES")
    print("=" * 80)
    
    for req in test_requirements:
        print(f"\n{'='*60}")
        print(f"Requirement: {req.id}")
        print(f"Category: {req.category.value}")
        print(f"Description length: {len(req.description)} chars")
        print(f"Description: {req.description[:150]}...")
        
        # Get matches
        matches = matcher.match_requirement(req, top_n=5, min_score=0.0)
        
        print(f"\nMatches found: {len(matches)}")
        if matches:
            print("\nTop matches:")
            for i, match in enumerate(matches[:3], 1):
                print(f"\n{i}. {match.service_name} - {match.score:.1%}")
                print(f"   Category: {match.service_category.value}")
                print(f"   Reasoning: {match.reasoning}")
        else:
            print("❌ No matches found!")
    
    # Now test with actual problematic requirement
    print("\n" + "=" * 80)
    print("TESTING WITH TYPICAL AI-EXTRACTED REQUIREMENT")
    print("=" * 80)
    
    typical_req = Requirement(
        id="typical",
        rfp_id="test",
        description="""Complete Testing and QA, including automated tests, load testing, and security testing. 
        The testing approach must ensure 80%+ code coverage and include regression testing for all deployments. 
        Performance testing should validate the system can handle 10,000 concurrent users. 
        Security testing must follow OWASP Top 10 guidelines and include penetration testing.""",
        category=RequirementCategory.TECHNICAL,
        priority=RequirementPriority.HIGH,
        confidence=0.98
    )
    
    print(f"\nDescription: {typical_req.description}")
    print(f"Length: {len(typical_req.description)} chars")
    print(f"Word count: {len(typical_req.description.split())} words")
    
    matches = matcher.match_requirement(typical_req, top_n=5, min_score=0.0)
    
    print(f"\n{'='*40}")
    print(f"Matches: {len(matches)}")
    print(f"{'='*40}")
    
    if matches:
        for i, match in enumerate(matches, 1):
            print(f"\n{i}. {match.service_name}")
            print(f"   Score: {match.score:.1%} ({match.score:.4f})")
            print(f"   Category: {match.service_category.value}")
            print(f"   Reasoning: {match.reasoning}")
            
            # Show if it would be filtered at different thresholds
            if match.score >= 0.80:
                print(f"   ✅ Would show at 80% threshold (strong match)")
            elif match.score >= 0.50:
                print(f"   🟡 Would show at 50% threshold (moderate match)")
            else:
                print(f"   🔴 Would be filtered at 50% threshold (weak match)")
    else:
        print("\n❌ NO MATCHES FOUND - This is the problem!")
        print("\nPossible causes:")
        print("1. Requirement description too long/diluted")
        print("2. No keyword overlap with services")
        print("3. TF-IDF penalizing common words")
    
    print("\n" + "=" * 80)
    print("DIAGNOSIS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    test_matching()

