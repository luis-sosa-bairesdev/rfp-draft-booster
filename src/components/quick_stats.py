"""
Quick Stats component for Welcome page.

This component displays current RFP statistics and provides
a demo RFP loader for preview purposes.
"""

import logging
import streamlit as st
from datetime import datetime, timedelta
from typing import Optional, Dict

from src.models.rfp import RFP
from src.models.requirement import (
    Requirement,
    RequirementCategory,
    RequirementPriority
)
from src.models.risk import Risk, RiskCategory, RiskSeverity

logger = logging.getLogger(__name__)


def get_quick_stats() -> Optional[Dict]:
    """
    Get current RFP statistics from session_state.
    
    Returns:
        Dictionary with stats if RFP loaded, None otherwise.
        Stats include:
        - total_requirements
        - risks_flagged (critical + high)
        - draft_completeness
        - rfp_pages
        - avg_confidence
        - service_matches_pct (if available)
    """
    # Check if RFP loaded
    if not st.session_state.get("rfp"):
        logger.debug("No RFP loaded, returning None for quick stats")
        return None
    
    try:
        rfp = st.session_state.rfp
        requirements = st.session_state.get("requirements", [])
        risks = st.session_state.get("risks", [])
        draft = st.session_state.get("draft")
        
        # Calculate basic stats
        stats = {
            "total_requirements": len(requirements),
            "risks_flagged": len([
                r for r in risks
                if r.severity in [RiskSeverity.CRITICAL, RiskSeverity.HIGH]
            ]),
            "draft_completeness": (
                draft.completeness_score if draft and hasattr(draft, 'completeness_score')
                else 0
            ),
            "rfp_pages": (
                rfp.total_pages if rfp.total_pages > 0
                else len(rfp.extracted_text.split('\n\n')) if rfp.extracted_text
                else 0
            ),
            "avg_confidence": (
                sum(r.confidence for r in requirements) / len(requirements)
                if requirements else 0.0
            )
        }
        
        # Add service matches if available
        if "service_matches" in st.session_state and st.session_state.service_matches:
            matches = st.session_state.service_matches
            approved = [
                m for m in matches
                if m.get("approved", False) and m.get("fit_percentage", 0) > 80
            ]
            stats["service_matches_pct"] = (
                (len(approved) / len(matches) * 100) if matches else 0
            )
        
        logger.debug(f"Quick stats calculated: {stats}")
        return stats
    
    except Exception as e:
        logger.error(f"Error calculating quick stats: {e}", exc_info=True)
        return None


def load_demo_rfp():
    """Load demo RFP data for Quick Stats preview."""
    logger.info("Loading demo RFP data")
    
    try:
        # Create demo RFP
        demo_rfp = RFP(
            id="demo-rfp-001",
            file_name="demo_rfp_software_development.pdf",
            title="Software Development RFP - Demo",
            client_name="ABC Corporation",
            deadline=datetime.now() + timedelta(days=30),
            notes="This is a demo RFP for preview purposes. Real data would come from uploaded PDFs.",
            extracted_text="""
            ABC Corporation seeks proposals for a cloud-based enterprise software solution.
            
            Key Requirements:
            - Microservices architecture
            - 99.9% uptime SLA
            - Real-time data processing
            - Advanced security features
            - Multi-tenant support
            - API-first design
            - Scalable infrastructure
            - Comprehensive documentation
            - 24/7 support
            - Integration with existing systems
            
            The solution must handle 1 million daily transactions and support 10,000 concurrent users.
            """,
            total_pages=50,
            upload_date=datetime.now()
        )
        
        # Create demo requirements
        demo_requirements = [
            Requirement(
                id="req-demo-001",
                description="Cloud-based microservices architecture required",
                category=RequirementCategory.TECHNICAL,
                priority=RequirementPriority.CRITICAL,
                page_number=5,
                confidence=0.95,
                verified=True
            ),
            Requirement(
                id="req-demo-002",
                description="99.9% uptime SLA guarantee",
                category=RequirementCategory.FUNCTIONAL,
                priority=RequirementPriority.HIGH,
                page_number=7,
                confidence=0.92,
                verified=True
            ),
            Requirement(
                id="req-demo-003",
                description="Real-time data processing capabilities",
                category=RequirementCategory.PERFORMANCE,
                priority=RequirementPriority.HIGH,
                page_number=9,
                confidence=0.88,
                verified=True
            ),
            Requirement(
                id="req-demo-004",
                description="Advanced security features and encryption",
                category=RequirementCategory.SECURITY,
                priority=RequirementPriority.CRITICAL,
                page_number=11,
                confidence=0.91,
                verified=True
            ),
            Requirement(
                id="req-demo-005",
                description="Multi-tenant support with data isolation",
                category=RequirementCategory.TECHNICAL,
                priority=RequirementPriority.HIGH,
                page_number=13,
                confidence=0.89,
                verified=True
            ),
            Requirement(
                id="req-demo-006",
                description="API-first design with RESTful endpoints",
                category=RequirementCategory.INTEGRATION,
                priority=RequirementPriority.HIGH,
                page_number=15,
                confidence=0.93,
                verified=True
            ),
            Requirement(
                id="req-demo-007",
                description="Scalable infrastructure to handle growth",
                category=RequirementCategory.PERFORMANCE,
                priority=RequirementPriority.HIGH,
                page_number=17,
                confidence=0.90,
                verified=False
            ),
            Requirement(
                id="req-demo-008",
                description="Comprehensive technical documentation",
                category=RequirementCategory.COMPLIANCE,
                priority=RequirementPriority.MEDIUM,
                page_number=19,
                confidence=0.85,
                verified=True
            ),
            Requirement(
                id="req-demo-009",
                description="24/7 technical support and monitoring",
                category=RequirementCategory.OPERATIONAL,
                priority=RequirementPriority.HIGH,
                page_number=21,
                confidence=0.87,
                verified=True
            ),
            Requirement(
                id="req-demo-010",
                description="Integration with existing enterprise systems",
                category=RequirementCategory.INTEGRATION,
                priority=RequirementPriority.HIGH,
                page_number=23,
                confidence=0.88,
                verified=True
            ),
            Requirement(
                id="req-demo-011",
                description="Handle 1 million daily transactions",
                category=RequirementCategory.PERFORMANCE,
                priority=RequirementPriority.CRITICAL,
                page_number=25,
                confidence=0.94,
                verified=True
            ),
            Requirement(
                id="req-demo-012",
                description="Support 10,000 concurrent users",
                category=RequirementCategory.PERFORMANCE,
                priority=RequirementPriority.CRITICAL,
                page_number=25,
                confidence=0.93,
                verified=True
            ),
            Requirement(
                id="req-demo-013",
                description="Data backup and disaster recovery",
                category=RequirementCategory.COMPLIANCE,
                priority=RequirementPriority.HIGH,
                page_number=27,
                confidence=0.90,
                verified=True
            ),
            Requirement(
                id="req-demo-014",
                description="Compliance with GDPR and SOC 2",
                category=RequirementCategory.COMPLIANCE,
                priority=RequirementPriority.CRITICAL,
                page_number=29,
                confidence=0.91,
                verified=True
            ),
            Requirement(
                id="req-demo-015",
                description="Automated deployment and CI/CD pipeline",
                category=RequirementCategory.TECHNICAL,
                priority=RequirementPriority.MEDIUM,
                page_number=31,
                confidence=0.86,
                verified=False
            )
        ]
        
        # Create demo risks
        demo_risks = [
            Risk(
                id="risk-demo-001",
                clause_text="Payment terms net-90 days from invoice",
                category=RiskCategory.FINANCIAL,
                severity=RiskSeverity.HIGH,
                confidence=0.88,
                page_number=35,
                recommendation="Negotiate for net-30 terms to improve cash flow",
                acknowledged=False
            ),
            Risk(
                id="risk-demo-002",
                clause_text="Unlimited liability clause for data breaches",
                category=RiskCategory.LEGAL,
                severity=RiskSeverity.CRITICAL,
                confidence=0.92,
                page_number=37,
                recommendation="Request liability cap and insurance requirements",
                acknowledged=False
            ),
            Risk(
                id="risk-demo-003",
                clause_text="3-month implementation deadline",
                category=RiskCategory.TIMELINE,
                severity=RiskSeverity.HIGH,
                confidence=0.85,
                page_number=39,
                recommendation="Negotiate 6-month timeline for proper implementation",
                acknowledged=False
            ),
            Risk(
                id="risk-demo-004",
                clause_text="Exclusive vendor lock-in for 5 years",
                category=RiskCategory.CONTRACTUAL,
                severity=RiskSeverity.MEDIUM,
                confidence=0.81,
                page_number=41,
                recommendation="Negotiate shorter term or exit clauses",
                acknowledged=False
            ),
            Risk(
                id="risk-demo-005",
                clause_text="Penalties up to 20% for SLA breaches",
                category=RiskCategory.FINANCIAL,
                severity=RiskSeverity.CRITICAL,
                confidence=0.90,
                page_number=43,
                recommendation="Request reasonable penalty caps and force majeure clauses",
                acknowledged=False
            ),
            Risk(
                id="risk-demo-006",
                clause_text="Client may terminate with 30 days notice",
                category=RiskCategory.CONTRACTUAL,
                severity=RiskSeverity.HIGH,
                confidence=0.87,
                page_number=45,
                recommendation="Negotiate mutual termination terms and transition period",
                acknowledged=False
            ),
            Risk(
                id="risk-demo-007",
                clause_text="All source code becomes client property",
                category=RiskCategory.LEGAL,
                severity=RiskSeverity.MEDIUM,
                confidence=0.83,
                page_number=47,
                recommendation="Clarify IP rights and retain reusable component ownership",
                acknowledged=False
            )
        ]
        
        # Update session_state
        st.session_state.rfp = demo_rfp
        st.session_state.requirements = demo_requirements
        st.session_state.risks = demo_risks
        st.session_state.draft = None  # No draft for demo
        
        logger.info(
            f"Demo RFP loaded: {len(demo_requirements)} requirements, "
            f"{len(demo_risks)} risks"
        )
    
    except Exception as e:
        logger.error(f"Error loading demo RFP: {e}", exc_info=True)
        st.error("⚠️ Error loading demo RFP. Please try again.")


def render_quick_stats():
    """Render Quick Stats section on Welcome page."""
    st.markdown("---")
    st.subheader("📊 Quick Stats")
    
    stats = get_quick_stats()
    
    if stats is None:
        # No RFP loaded - show placeholder
        st.info(
            "📤 **Upload an RFP** to see your project statistics. "
            "Or click 'See Example RFP' above to load demo data."
        )
        
        # Show example stats
        with st.expander("📝 Example Stats (Demo RFP)"):
            example_col1, example_col2, example_col3 = st.columns(3)
            example_col1.metric("Requirements", "15")
            example_col2.metric("Risks Flagged", "7")
            example_col3.metric("Draft Complete", "100%")
            
            st.caption("💡 These are example values. Load a real RFP to see your actual stats.")
    
    else:
        # RFP loaded - show real stats with navigation
        st.markdown("**Current RFP Statistics**")
        
        # First row of metrics
        stat_col1, stat_col2, stat_col3 = st.columns(3)
        
        with stat_col1:
            st.metric(
                "Total Requirements",
                stats["total_requirements"],
                help="Number of requirements extracted from RFP"
            )
            if st.button(
                "View Requirements →",
                key="stats_goto_reqs",
                help="Navigate to Requirements page"
            ):
                st.switch_page("pages/2_📋_Requirements.py")
        
        with stat_col2:
            st.metric(
                "Risks Flagged",
                stats["risks_flagged"],
                help="Critical and high-severity risks identified"
            )
            if st.button(
                "View Risks →",
                key="stats_goto_risks",
                help="Navigate to Risk Analysis page"
            ):
                st.switch_page("pages/3_⚠️_Risk_Analysis.py")
        
        with stat_col3:
            st.metric(
                "Draft Completeness",
                f"{stats['draft_completeness']:.0f}%",
                help="Percentage of required sections completed"
            )
            if st.button(
                "View Draft →",
                key="stats_goto_draft",
                help="Navigate to Draft Generation page"
            ):
                st.switch_page("pages/5_✍️_Draft_Generation.py")
        
        # Second row of metrics
        stat_col4, stat_col5, stat_col6 = st.columns(3)
        
        with stat_col4:
            st.metric(
                "RFP Pages",
                stats["rfp_pages"],
                help="Number of pages in the uploaded RFP"
            )
        
        with stat_col5:
            st.metric(
                "Avg Confidence",
                f"{stats['avg_confidence']:.0%}",
                help="Average confidence score of extracted requirements"
            )
        
        with stat_col6:
            if "service_matches_pct" in stats:
                st.metric(
                    "Service Matches",
                    f"{stats['service_matches_pct']:.0f}%",
                    help="Percentage of high-quality service matches"
                )
            else:
                st.metric(
                    "Service Matches",
                    "N/A",
                    help="Run Service Matching to see this metric"
                )

