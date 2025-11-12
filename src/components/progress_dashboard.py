"""
Progress Dashboard Component - Shows overall RFP analysis progress.
"""

import streamlit as st
from typing import List, Optional
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import Requirement, Risk, RequirementCategory, RiskSeverity


def render_progress_dashboard(
    requirements: Optional[List[Requirement]] = None,
    risks: Optional[List[Risk]] = None
):
    """Render progress dashboard with metrics."""
    
    requirements = requirements or []
    risks = risks or []
    
    st.markdown("### 📊 Progress Dashboard")
    
    # Requirements metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Requirements", len(requirements))
    
    with col2:
        if requirements:
            verified = sum(1 for r in requirements if r.verified)
            st.metric("Verified", f"{verified}/{len(requirements)}")
        else:
            st.metric("Verified", "0/0")
    
    with col3:
        st.metric("Risks Detected", len(risks))
    
    with col4:
        if risks:
            acknowledged = sum(1 for r in risks if r.acknowledged)
            st.metric("Risks Acknowledged", f"{acknowledged}/{len(risks)}")
        else:
            st.metric("Risks Acknowledged", "0/0")
    
    # Requirements by category
    if requirements:
        st.markdown("#### Requirements by Category")
        by_category = {}
        for req in requirements:
            cat = req.category.value if hasattr(req.category, 'value') else str(req.category)
            by_category[cat] = by_category.get(cat, 0) + 1
        
        cols = st.columns(len(by_category))
        for i, (cat, count) in enumerate(by_category.items()):
            with cols[i]:
                st.metric(cat.title(), count)
    
    # Risks by severity
    if risks:
        st.markdown("#### Risks by Severity")
        by_severity = {}
        for risk in risks:
            sev = risk.severity.value if hasattr(risk.severity, 'value') else str(risk.severity)
            by_severity[sev] = by_severity.get(sev, 0) + 1
        
        cols = st.columns(len(by_severity))
        for i, (sev, count) in enumerate(by_severity.items()):
            with cols[i]:
                # Color coding
                color_map = {
                    "critical": "🔴",
                    "high": "🟠",
                    "medium": "🟡",
                    "low": "🟢"
                }
                icon = color_map.get(sev, "⚠️")
                st.metric(f"{icon} {sev.title()}", count)
        
        # Critical risks warning
        critical_unacknowledged = [
            r for r in risks 
            if r.severity.value == "critical" and not r.acknowledged
        ]
        if critical_unacknowledged:
            st.warning(f"⚠️ {len(critical_unacknowledged)} critical risk(s) not acknowledged")
    
    # Progress bars
    st.markdown("#### Overall Progress")
    
    # Requirements progress
    if requirements:
        verified_pct = sum(1 for r in requirements if r.verified) / len(requirements)
        st.progress(verified_pct, text=f"Requirements Verified: {verified_pct:.0%}")
    
    # Risks progress
    if risks:
        acknowledged_pct = sum(1 for r in risks if r.acknowledged) / len(risks)
        st.progress(acknowledged_pct, text=f"Risks Acknowledged: {acknowledged_pct:.0%}")

