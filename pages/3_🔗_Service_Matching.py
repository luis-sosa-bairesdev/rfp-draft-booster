"""Service Matching page - Match requirements to BairesDev services."""

import streamlit as st
import pandas as pd
from typing import List

from models import Service, Requirement
from models.service import load_services_from_json, get_default_services
from services.service_matcher import ServiceMatcher, ServiceMatch
from src.utils.logger import setup_logger
from src.utils.error_handler import handle_error, ValidationError
from utils.session import init_session_state, has_current_rfp
from components.ai_assistant import render_ai_assistant_button, render_ai_assistant_modal
from components.navigation_flow import render_navigation_buttons

logger = setup_logger(__name__)


def load_services() -> List[Service]:
    """Load services from JSON file."""
    try:
        services = load_services_from_json("data/services.json")
        logger.info(f"Loaded {len(services)} services from JSON")
        return services
    except Exception as e:
        logger.warning(f"Failed to load services from JSON: {e}. Using defaults.")
        return get_default_services()


def compute_matches(
    requirements: List[Requirement],
    services: List[Service],
    min_score: float = 0.3,
    top_n: int = 3
) -> List[ServiceMatch]:
    """Compute service matches for requirements."""
    if not requirements or not services:
        return []
    
    matcher = ServiceMatcher(services)
    matches = matcher.match_all_requirements(
        requirements,
        top_n=top_n,
        min_score=min_score
    )
    
    return matches


def render_header_stats(
    requirements: List[Requirement],
    services: List[Service],
    matches: List[ServiceMatch],
    matcher: ServiceMatcher
):
    """Render header with statistics."""
    st.title("🔗 Service Matching")
    st.markdown("Match RFP requirements to BairesDev services automatically")
    
    st.markdown("---")
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Requirements", len(requirements))
    
    with col2:
        st.metric("Services", len(services))
    
    with col3:
        avg_coverage = matcher.get_overall_coverage(matches) if matches else 0.0
        st.metric("Avg Match", f"{avg_coverage:.0%}")
    
    with col4:
        approved, total = matcher.count_approved_matches(matches)
        st.metric("Approved", f"{approved}/{total}")


def render_filters(key_suffix: str = ""):
    """Render filter controls."""
    st.markdown("### 🔍 Filters")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Category filter
        categories = ["All", "Technical", "Functional", "Timeline", "Budget", "Compliance"]
        category_filter = st.selectbox(
            "Filter by Category",
            categories,
            key=f"filter_category_{key_suffix}"
        )
    
    with col2:
        # Match % threshold
        min_score = st.slider(
            "Minimum Match %",
            min_value=0,
            max_value=100,
            value=40,  # Lowered from 50 to be more permissive
            step=10,
            key=f"filter_score_{key_suffix}",
            help="Show only matches above this threshold"
        ) / 100.0
    
    with col3:
        # Sort order
        sort_options = ["Highest Match First", "Lowest Match First", "Requirement Order"]
        sort_order = st.selectbox(
            "Sort By",
            sort_options,
            key=f"filter_sort_{key_suffix}"
        )
    
    return category_filter, min_score, sort_order


def filter_and_sort_matches(
    matches: List[ServiceMatch],
    category_filter: str,
    min_score: float,
    sort_order: str
) -> List[ServiceMatch]:
    """Apply filters and sorting to matches."""
    filtered = matches
    
    # Apply category filter
    if category_filter != "All":
        filtered = [
            m for m in filtered
            if m.requirement_category.value.lower() == category_filter.lower()
        ]
    
    # Apply score filter
    filtered = [m for m in filtered if m.score >= min_score]
    
    # Apply sorting
    if sort_order == "Highest Match First":
        filtered = sorted(filtered, key=lambda m: m.score, reverse=True)
    elif sort_order == "Lowest Match First":
        filtered = sorted(filtered, key=lambda m: m.score)
    # "Requirement Order" keeps current order
    
    return filtered


def render_matches_table(
    matches: List[ServiceMatch],
    matcher: ServiceMatcher,
    key_suffix: str = ""
):
    """Render matches table with approval checkboxes."""
    if not matches:
        st.info("📭 No matches found with current filters. Try lowering the minimum match threshold.")
        return
    
    st.markdown(f"### 📊 Matches ({len(matches)})")
    
    # Build dataframe for display
    rows = []
    for i, match in enumerate(matches):
        color_indicator = matcher.color_for_score(match.score)
        
        rows.append({
            "": color_indicator,
            "Req ID": match.requirement_id[:8],
            "Requirement": match.requirement_description[:60] + "..." if len(match.requirement_description) > 60 else match.requirement_description,
            "Category": match.requirement_category.value.title(),
            "Matched Service": match.service_name,
            "Match %": f"{match.score:.0%}",
            "Reasoning": match.reasoning[:80] + "..." if len(match.reasoning) > 80 else match.reasoning,
            "_index": i  # Hidden column for tracking
        })
    
    df = pd.DataFrame(rows)
    
    # Display table (read-only for now, approval checkboxes below)
    st.dataframe(
        df.drop(columns=["_index"]),
        use_container_width=True,
        hide_index=True
    )
    
    # Expandable details
    with st.expander("📋 View Full Details"):
        for i, match in enumerate(matches):
            color_indicator = matcher.color_for_score(match.score)
            
            st.markdown(f"**{color_indicator} Match {i+1}: {match.service_name}** ({match.score:.0%})")
            st.markdown(f"**Requirement:** {match.requirement_description}")
            st.markdown(f"**Category:** {match.requirement_category.value.title()} → {match.service_category.value.title()}")
            st.markdown(f"**Reasoning:** {match.reasoning}")
            
            # Approval checkbox
            is_approved = st.checkbox(
                "✅ Approve this match",
                value=match.approved,
                key=f"approve_{match.requirement_id}_{match.service_id}_{key_suffix}"
            )
            
            # Update approval status in session state
            if is_approved != match.approved:
                match.approved = is_approved
                # Update session state
                for m in st.session_state.service_matches:
                    if (m.requirement_id == match.requirement_id and 
                        m.service_id == match.service_id):
                        m.approved = is_approved
                
                st.rerun()
            
            st.markdown("---")


def render_bulk_actions(matches: List[ServiceMatch], matcher: ServiceMatcher, key_suffix: str = ""):
    """Render bulk action buttons."""
    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
        if st.button("✅ Approve All High (>80%)", key=f"btn_approve_high_{key_suffix}"):
            for match in matches:
                if match.score >= 0.80:
                    match.approved = True
                    # Update in session state
                    for m in st.session_state.service_matches:
                        if (m.requirement_id == match.requirement_id and 
                            m.service_id == match.service_id):
                            m.approved = True
            
            st.success(f"✅ Approved {sum(1 for m in matches if m.score >= 0.80)} high-confidence matches")
            st.rerun()
    
    with col2:
        if st.button("❌ Clear All Approvals", key=f"btn_clear_all_{key_suffix}"):
            for match in matches:
                match.approved = False
                # Update in session state
                for m in st.session_state.service_matches:
                    if (m.requirement_id == match.requirement_id and 
                        m.service_id == match.service_id):
                        m.approved = False
            
            st.info("❌ Cleared all approvals")
            st.rerun()
    
    with col3:
        # Export functionality
        render_export_button(matches, matcher, key_suffix)


def render_export_button(matches: List[ServiceMatch], matcher: ServiceMatcher, key_suffix: str = ""):
    """Render export matches button."""
    import json
    from datetime import datetime
    
    # Option to export approved only
    export_approved_only = st.checkbox(
        "Approved Only",
        value=False,
        key=f"export_approved_only_{key_suffix}",
        help="Export only approved matches"
    )
    
    # Filter matches if needed
    export_matches = [m for m in matches if m.approved] if export_approved_only else matches
    
    if not export_matches:
        st.warning("No matches to export")
        return
    
    # Prepare export data
    rfp = st.session_state.get("rfp")
    rfp_id = rfp.id if rfp else "unknown"
    
    coverage = matcher.calculate_coverage_by_category(export_matches)
    overall_coverage = matcher.get_overall_coverage(export_matches)
    
    export_data = {
        "rfp_id": rfp_id,
        "exported_at": datetime.now().isoformat(),
        "total_matches": len(export_matches),
        "approved_matches": sum(1 for m in export_matches if m.approved),
        "matches": [m.to_dict() for m in export_matches],
        "coverage": {cat: f"{score:.2%}" for cat, score in coverage.items()},
        "overall_coverage": f"{overall_coverage:.2%}"
    }
    
    # Generate JSON
    json_str = json.dumps(export_data, indent=2)
    
    # Download button
    filename = f"service_matches_rfp-{rfp_id}_{datetime.now().strftime('%Y%m%d')}.json"
    
    st.download_button(
        label="📥 Export Matches",
        data=json_str,
        file_name=filename,
        mime="application/json",
        key=f"btn_export_{key_suffix}",
        use_container_width=True
    )


def render_coverage_chart(matches: List[ServiceMatch], matcher: ServiceMatcher):
    """Render coverage bar chart by requirement category."""
    st.markdown("### 📊 Coverage by Category")
    
    # Calculate coverage
    coverage = matcher.calculate_coverage_by_category(matches)
    
    if not coverage:
        st.info("No coverage data available")
        return
    
    # Prepare data for chart
    categories = list(coverage.keys())
    scores = [coverage[cat] * 100 for cat in categories]  # Convert to percentage
    
    # Create DataFrame for bar chart
    chart_data = pd.DataFrame({
        "Category": [cat.title() for cat in categories],
        "Match %": scores
    })
    
    # Display bar chart
    st.bar_chart(chart_data.set_index("Category"))
    
    # Overall average
    overall = matcher.get_overall_coverage(matches)
    st.caption(f"📈 **Overall Average Match:** {overall:.0%}")
    
    # Add interpretation
    if overall >= 0.80:
        st.success("✅ Excellent coverage! Most requirements have strong service matches.")
    elif overall >= 0.60:
        st.info("ℹ️ Good coverage. Some requirements may need manual review.")
    elif overall >= 0.40:
        st.warning("⚠️ Moderate coverage. Consider expanding service catalog or refining requirements.")
    else:
        st.error("❌ Low coverage. Many requirements lack strong service matches.")


def render_empty_state():
    """Render empty state when no requirements exist."""
    st.info("📋 **No Requirements Found**")
    st.markdown("""
    To use Service Matching, you need to:
    1. Upload an RFP (📤 Upload RFP page)
    2. Extract requirements (📋 Requirements page)
    3. Return here to see service matches
    """)
    
    if st.button("Go to Requirements Page"):
        st.switch_page("pages/2_📋_Requirements.py")


def main():
    """Main Service Matching page."""
    
    # Initialize session
    init_session_state()
    
    # Render AI Assistant modal FIRST if open
    if st.session_state.get("show_ai_assistant", False):
        render_ai_assistant_modal(key_suffix="service_matching", page_context="service_matching")
        st.markdown("---")
    
    # Check prerequisites
    if not has_current_rfp():
        st.warning("⚠️ Please upload an RFP first")
        if st.button("Go to Upload Page"):
            st.switch_page("pages/1_📤_Upload_RFP.py")
        return
    
    # Get requirements
    requirements = st.session_state.get("requirements", [])
    
    if not requirements:
        render_empty_state()
        return
    
    # Load services
    if not st.session_state.get("services"):
        st.session_state.services = load_services()
    
    services = st.session_state.services
    
    # Compute matches if not already computed
    if not st.session_state.get("service_matches"):
        with st.spinner("🔍 Computing service matches..."):
            matches = compute_matches(requirements, services, min_score=0.3, top_n=3)
            st.session_state.service_matches = matches
            logger.info(f"Computed {len(matches)} matches")
    
    matches = st.session_state.service_matches
    
    # Initialize matcher for stats
    matcher = ServiceMatcher(services)
    
    # Render header
    render_header_stats(requirements, services, matches, matcher)
    
    st.markdown("---")
    
    # Render filters
    category_filter, min_score, sort_order = render_filters(key_suffix="main")
    
    st.markdown("---")
    
    # Apply filters and sorting
    filtered_matches = filter_and_sort_matches(matches, category_filter, min_score, sort_order)
    
    # Render bulk actions
    if filtered_matches:
        render_bulk_actions(filtered_matches, matcher, key_suffix="main")
        st.markdown("---")
    
    # Render matches table
    render_matches_table(filtered_matches, matcher, key_suffix="main")
    
    # Render coverage chart
    if matches:
        st.markdown("---")
        render_coverage_chart(matches, matcher)
    
    # AI Assistant button in sidebar
    with st.sidebar:
        st.markdown("---")
        render_ai_assistant_button(key_suffix="service_matching")

    # Navigation buttons
    render_navigation_buttons('matching')


if __name__ == "__main__":
    main()

