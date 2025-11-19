"""
ROI Calculator page.

This page provides an interactive ROI calculator to estimate time and cost
savings from using RFP Draft Booster. If an RFP is loaded, users can calculate
ROI based on the actual RFP data or use generic inputs.
"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import settings
from utils.session import get_current_rfp
from components.roi_calculator import (
    render_roi_calculator,
    init_roi_session_state,
    DEFAULT_RFP_PAGES,
    DEFAULT_HOURLY_RATE,
    DEFAULT_TIME_PER_PAGE
)
from components.ai_assistant import render_ai_assistant_button, render_ai_assistant_modal
from utils.calculations import calculate_full_roi

# Page configuration
st.set_page_config(
    page_title=f"ROI Calculator - {settings.app_name}",
    page_icon="💰",
    layout="wide"
)

# Initialize session state
init_roi_session_state()


def calculate_rfp_roi(rfp):
    """
    Calculate ROI based on actual RFP data.
    
    Args:
        rfp: RFP object with real data
    
    Returns:
        dict: ROI metrics
    """
    # Get actual RFP pages
    rfp_pages = rfp.total_pages if rfp.total_pages > 0 else DEFAULT_RFP_PAGES
    
    # Get hourly rate from session or use default
    hourly_rate = st.session_state.get("roi_hourly_rate", DEFAULT_HOURLY_RATE)
    
    # Get time per page from session or use default
    time_per_page = st.session_state.get("roi_time_per_page", DEFAULT_TIME_PER_PAGE)
    
    # Calculate ROI
    metrics = calculate_full_roi(
        rfp_pages=rfp_pages,
        time_per_page=time_per_page,
        hourly_rate=hourly_rate,
        rfps_per_month=10
    )
    
    return metrics, rfp_pages


def render_rfp_based_calculator(rfp):
    """Render ROI calculator using actual RFP data."""
    
    st.info(
        f"📄 **Calculating ROI for:** {rfp.client_name or rfp.file_name}\n\n"
        f"Using real data from your uploaded RFP. You can still adjust the hourly rate "
        f"and time estimates below."
    )
    
    # RFP-specific info box
    with st.expander("📊 Current RFP Details", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "RFP Pages",
                rfp.total_pages if rfp.total_pages > 0 else "N/A",
                help="Actual number of pages in your RFP"
            )
        
        with col2:
            st.metric(
                "Client",
                rfp.client_name or "Not specified",
                help="Client name from RFP"
            )
        
        with col3:
            requirements_count = len(st.session_state.get("requirements", []))
            st.metric(
                "Requirements",
                requirements_count,
                help="Requirements extracted from RFP"
            )
    
    st.markdown("---")
    
    # Adjustable parameters (only hourly rate and time per page)
    st.subheader("💵 Adjust Your Team's Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        hourly_rate = st.slider(
            "💵 Team Hourly Rate ($)",
            min_value=50,
            max_value=200,
            value=st.session_state.get("roi_hourly_rate", DEFAULT_HOURLY_RATE),
            step=10,
            key="rfp_hourly_rate",
            help="Average cost per hour for your proposal team"
        )
        st.session_state.roi_hourly_rate = hourly_rate
    
    with col2:
        time_per_page = st.slider(
            "⏱️ Manual Time per Page (hours)",
            min_value=1.0,
            max_value=5.0,
            value=st.session_state.get("roi_time_per_page", DEFAULT_TIME_PER_PAGE),
            step=0.5,
            key="rfp_time_per_page",
            help="Average time to manually process one page"
        )
        st.session_state.roi_time_per_page = time_per_page
    
    # Calculate and display metrics
    metrics, rfp_pages = calculate_rfp_roi(rfp)
    
    st.markdown("---")
    st.markdown("### 📈 Your ROI for This RFP")
    
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    
    with metric_col1:
        st.metric(
            label="⏱️ Time Saved",
            value=f"{metrics['time_saved']:.1f} hours",
            delta=f"↓{metrics['time_reduction_pct']:.0f}% faster",
            delta_color="normal",
            help=f"Time saved processing this {rfp_pages}-page RFP"
        )
    
    with metric_col2:
        st.metric(
            label="💰 Cost Savings",
            value=f"${metrics['cost_saved']:,.0f}",
            delta="Per RFP",
            delta_color="normal",
            help="Cost savings for this specific RFP"
        )
    
    with metric_col3:
        st.metric(
            label="📊 Potential Monthly ROI",
            value=f"${metrics['roi_monthly']:,.0f}",
            delta="10 RFPs/month",
            delta_color="normal",
            help="If you process 10 similar RFPs per month"
        )
    
    st.caption(
        f"💡 **Annual ROI:** ${metrics['roi_annual']:,.0f} "
        f"(120 RFPs/year) • "
        f"**Manual:** ${metrics['cost_manual']:,.0f} • "
        f"**Automated:** ${metrics['cost_automated']:,.0f}"
    )
    
    # Comparison table
    st.markdown("---")
    with st.expander("📋 Detailed Breakdown"):
        import pandas as pd
        
        comparison_data = {
            "Metric": [
                "Total Pages",
                "Time per Page",
                "Manual Time",
                "Automated Time",
                "Time Saved",
                "Hourly Rate",
                "Manual Cost",
                "Automated Cost",
                "Cost Saved",
                "ROI (Monthly)",
                "ROI (Annual)"
            ],
            "Value": [
                f"{rfp_pages} pages",
                f"{time_per_page} hours",
                f"{metrics['manual_time']:.1f} hours",
                f"{metrics['automated_time']:.1f} hours",
                f"{metrics['time_saved']:.1f} hours",
                f"${hourly_rate}/hour",
                f"${metrics['cost_manual']:,.0f}",
                f"${metrics['cost_automated']:,.0f}",
                f"${metrics['cost_saved']:,.0f}",
                f"${metrics['roi_monthly']:,.0f}",
                f"${metrics['roi_annual']:,.0f}"
            ]
        }
        
        df = pd.DataFrame(comparison_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Export button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Export ROI Report",
            data=csv,
            file_name=f"roi_report_{rfp.file_name.replace('.pdf', '')}.csv",
            mime="text/csv",
            key="btn_export_rfp_roi"
        )


def main():
    """Main ROI Calculator page."""
    
    # Render AI Assistant modal if open
    if st.session_state.get("show_ai_assistant", False):
        render_ai_assistant_modal(key_suffix="roi", page_context="roi_calculator")
        st.markdown("---")
    
    # Header
    col1, col2 = st.columns([5, 1])
    with col1:
        st.title("💰 ROI Calculator")
        st.markdown(
            "**Estimate your savings** with AI-powered RFP processing. "
            "Calculate potential ROI based on your team's parameters."
        )
    with col2:
        render_ai_assistant_button(key_suffix="roi")
    
    st.divider()
    
    # Check if RFP is loaded
    rfp = get_current_rfp()
    
    if rfp:
        # RFP loaded - offer choice
        st.markdown("### 🎯 Choose Your Calculation Mode")
        
        calc_mode = st.radio(
            "Select how you want to calculate ROI:",
            options=[
                "📊 Calculate for Current RFP (uses real data)",
                "🧮 Generic Calculator (manual inputs)"
            ],
            key="roi_calc_mode",
            help=(
                "**Current RFP:** Uses actual page count from your uploaded RFP.\n\n"
                "**Generic:** Uses manual sliders for all parameters."
            )
        )
        
        st.markdown("---")
        
        if calc_mode.startswith("📊"):
            # RFP-based calculator
            render_rfp_based_calculator(rfp)
        else:
            # Generic calculator
            st.info(
                "🧮 **Generic Mode:** Adjust all parameters manually to estimate ROI "
                "for different scenarios."
            )
            render_roi_calculator()
    
    else:
        # No RFP loaded - generic calculator only
        st.info(
            "💡 **No RFP loaded yet.** Use the generic calculator below to estimate "
            "potential ROI. Upload an RFP to calculate ROI with real data!"
        )
        
        # Link to upload page
        col1, col2, col3 = st.columns([2, 3, 2])
        with col2:
            if st.button(
                "📤 Upload RFP to Get Real ROI",
                type="primary",
                use_container_width=True
            ):
                st.switch_page("pages/1_📤_Upload_RFP.py")
        
        st.markdown("---")
        
        # Generic calculator
        render_roi_calculator()
    
    # Footer with navigation
    st.markdown("---")
    st.markdown("### 🚀 Next Steps")
    
    nav_col1, nav_col2, nav_col3 = st.columns(3)
    
    with nav_col1:
        if st.button(
            "🏠 Back to Home",
            use_container_width=True,
            help="Return to Welcome page"
        ):
            st.switch_page("main.py")
    
    with nav_col2:
        if rfp:
            if st.button(
                "📋 View Requirements",
                use_container_width=True,
                help="See extracted requirements"
            ):
                st.switch_page("pages/2_📋_Requirements.py")
        else:
            st.button(
                "📋 View Requirements",
                use_container_width=True,
                disabled=True,
                help="Upload an RFP first"
            )
    
    with nav_col3:
        if rfp:
            if st.button(
                "✍️ Generate Draft",
                use_container_width=True,
                help="Create proposal draft"
            ):
                st.switch_page("pages/5_✍️_Draft_Generation.py")
        else:
            st.button(
                "✍️ Generate Draft",
                use_container_width=True,
                disabled=True,
                help="Upload an RFP first"
            )


if __name__ == "__main__":
    main()

