"""
ROI Calculator component for Welcome page.

This component provides an interactive ROI calculator with sliders
to estimate time and cost savings from using RFP Draft Booster.
"""

import logging
import pandas as pd
import streamlit as st
from typing import Optional

from src.utils.calculations import calculate_full_roi

logger = logging.getLogger(__name__)

# Default values
DEFAULT_RFP_PAGES = 50
DEFAULT_HOURLY_RATE = 100
DEFAULT_TIME_PER_PAGE = 2.0
DEFAULT_RFPS_PER_MONTH = 10

# Slider ranges
MIN_RFP_PAGES = 1
MAX_RFP_PAGES = 100
MIN_HOURLY_RATE = 50
MAX_HOURLY_RATE = 200
MIN_TIME_PER_PAGE = 1.0
MAX_TIME_PER_PAGE = 5.0
STEP_TIME_PER_PAGE = 0.5
STEP_HOURLY_RATE = 10


def init_roi_session_state():
    """Initialize ROI calculator session state variables."""
    if "roi_rfp_pages" not in st.session_state:
        st.session_state.roi_rfp_pages = DEFAULT_RFP_PAGES
    if "roi_hourly_rate" not in st.session_state:
        st.session_state.roi_hourly_rate = DEFAULT_HOURLY_RATE
    if "roi_time_per_page" not in st.session_state:
        st.session_state.roi_time_per_page = DEFAULT_TIME_PER_PAGE


def reset_roi_to_defaults():
    """Reset ROI calculator to default values."""
    st.session_state.roi_rfp_pages = DEFAULT_RFP_PAGES
    st.session_state.roi_hourly_rate = DEFAULT_HOURLY_RATE
    st.session_state.roi_time_per_page = DEFAULT_TIME_PER_PAGE
    logger.info("ROI calculator reset to defaults")


def generate_roi_report(
    rfp_pages: int,
    hourly_rate: float,
    time_per_page: float,
    metrics: dict
) -> str:
    """
    Generate CSV report of ROI calculation.
    
    Args:
        rfp_pages: Number of RFP pages
        hourly_rate: Team hourly rate
        time_per_page: Manual time per page
        metrics: Calculated ROI metrics
    
    Returns:
        CSV string
    """
    report_data = {
        "Metric": [
            "RFP Pages",
            "Team Hourly Rate",
            "Manual Time per Page",
            "Manual Time Total",
            "Automated Time",
            "Time Saved",
            "Time Reduction %",
            "Manual Cost",
            "Automated Cost",
            "Cost Saved per RFP",
            "ROI Monthly (10 RFPs)",
            "ROI Annual (120 RFPs)"
        ],
        "Value": [
            f"{rfp_pages} pages",
            f"${hourly_rate:.0f}/hour",
            f"{time_per_page} hours/page",
            f"{metrics['manual_time']:.1f} hours",
            f"{metrics['automated_time']:.1f} hours",
            f"{metrics['time_saved']:.1f} hours",
            f"{metrics['time_reduction_pct']:.0f}%",
            f"${metrics['cost_manual']:,.0f}",
            f"${metrics['cost_automated']:,.0f}",
            f"${metrics['cost_saved']:,.0f}",
            f"${metrics['roi_monthly']:,.0f}",
            f"${metrics['roi_annual']:,.0f}"
        ]
    }
    
    df_report = pd.DataFrame(report_data)
    csv = df_report.to_csv(index=False)
    
    logger.debug(f"Generated ROI report: {len(csv)} bytes")
    return csv


def render_roi_calculator():
    """Render the interactive ROI calculator component."""
    
    # Initialize session state
    init_roi_session_state()
    
    st.subheader("💰 ROI Calculator")
    st.markdown(
        "**Estimate your savings** with AI-powered RFP processing. "
        "Adjust the sliders below to see your potential ROI."
    )
    
    # Input sliders in 3 columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        rfp_pages = st.slider(
            "📄 RFP Pages",
            min_value=MIN_RFP_PAGES,
            max_value=MAX_RFP_PAGES,
            value=st.session_state.roi_rfp_pages,
            key="slider_rfp_pages",
            help="Average number of pages in your RFPs"
        )
    
    with col2:
        hourly_rate = st.slider(
            "💵 Team Hourly Rate ($)",
            min_value=MIN_HOURLY_RATE,
            max_value=MAX_HOURLY_RATE,
            value=st.session_state.roi_hourly_rate,
            step=STEP_HOURLY_RATE,
            key="slider_hourly_rate",
            help="Average cost per hour for your proposal team"
        )
    
    with col3:
        time_per_page = st.slider(
            "⏱️ Manual Time per Page (hours)",
            min_value=MIN_TIME_PER_PAGE,
            max_value=MAX_TIME_PER_PAGE,
            value=st.session_state.roi_time_per_page,
            step=STEP_TIME_PER_PAGE,
            key="slider_time_per_page",
            help="Average time to manually process one page"
        )
    
    # Update session state
    st.session_state.roi_rfp_pages = rfp_pages
    st.session_state.roi_hourly_rate = hourly_rate
    st.session_state.roi_time_per_page = time_per_page
    
    try:
        # Calculate ROI metrics
        metrics = calculate_full_roi(
            rfp_pages=rfp_pages,
            time_per_page=time_per_page,
            hourly_rate=hourly_rate,
            rfps_per_month=DEFAULT_RFPS_PER_MONTH
        )
        
        # Display metrics
        st.markdown("---")
        st.markdown("### 📈 Your Estimated Savings")
        
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        
        with metric_col1:
            st.metric(
                label="⏱️ Time Saved",
                value=f"{metrics['time_saved']:.1f} hours",
                delta=f"↓{metrics['time_reduction_pct']:.0f}% faster",
                delta_color="normal",
                help="Time saved per RFP with automation"
            )
        
        with metric_col2:
            st.metric(
                label="💰 Cost Savings",
                value=f"${metrics['cost_saved']:,.0f} /RFP",
                delta=f"+${metrics['cost_saved']:,.0f}",
                delta_color="normal",
                help="Cost savings per RFP"
            )
        
        with metric_col3:
            st.metric(
                label="📊 ROI Monthly",
                value=f"${metrics['roi_monthly']:,.0f}",
                delta=f"{DEFAULT_RFPS_PER_MONTH} RFPs/month",
                delta_color="normal",
                help="Monthly ROI based on average volume"
            )
        
        # Annual ROI caption
        st.caption(
            f"💡 **Annual ROI:** ${metrics['roi_annual']:,.0f} "
            f"(120 RFPs/year)"
        )
        
        # Optional visual comparison
        show_chart = st.checkbox(
            "📊 Show visual comparison",
            value=False,
            help="Display bar charts comparing manual vs. automated processing"
        )
        
        if show_chart:
            comparison_data = pd.DataFrame({
                "Process": ["Manual", "Automated"],
                "Time (hours)": [
                    metrics['manual_time'],
                    metrics['automated_time']
                ],
                "Cost (USD)": [
                    metrics['cost_manual'],
                    metrics['cost_automated']
                ]
            })
            
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                st.bar_chart(
                    comparison_data.set_index("Process")["Time (hours)"],
                    height=250
                )
                st.caption("⏱️ Time Comparison")
            
            with chart_col2:
                st.bar_chart(
                    comparison_data.set_index("Process")["Cost (USD)"],
                    height=250
                )
                st.caption("💰 Cost Comparison")
        
        # Action buttons
        st.markdown("---")
        action_col1, action_col2, action_col3 = st.columns([2, 2, 1])
        
        with action_col1:
            if st.button(
                "🔄 Reset to Defaults",
                key="btn_reset_roi",
                help="Reset all sliders to default values"
            ):
                reset_roi_to_defaults()
                st.rerun()
        
        with action_col2:
            # Generate CSV report
            csv_report = generate_roi_report(
                rfp_pages, hourly_rate, time_per_page, metrics
            )
            
            st.download_button(
                label="📥 Export ROI Report",
                data=csv_report,
                file_name="rfp_booster_roi_report.csv",
                mime="text/csv",
                key="btn_export_roi",
                help="Download detailed ROI report as CSV"
            )
        
        # Assumptions expander
        with st.expander("ℹ️ Calculation Assumptions"):
            st.markdown("""
            **How we calculate your savings:**
            
            - **80% time reduction:** Based on industry benchmarks for AI-assisted document processing
            - **10 RFPs per month:** Average for B2B sales teams and proposal departments
            
            **Manual process includes:**
            - Document review and extraction
            - Requirement identification and categorization
            - Risk assessment and analysis
            - Draft proposal writing
            - Multiple review cycles
            
            **Automated process (20% time):**
            - AI-powered extraction and analysis
            - Human review and validation
            - Final edits and approval
            
            **Formula:**
            ```
            Time Saved = RFP Pages × Time/Page × 80%
            Cost Saved = Time Saved × Hourly Rate
            ROI Monthly = Cost Saved × 10 RFPs/month
            ROI Annual = ROI Monthly × 12 months
            ```
            
            **Note:** Actual savings may vary based on RFP complexity, team experience, 
            and specific use cases. These estimates provide a conservative baseline.
            """)
    
    except Exception as e:
        logger.error(f"Error calculating ROI: {e}", exc_info=True)
        st.error("⚠️ Error calculating ROI. Please check your inputs and try again.")


def render_cta_section():
    """Render call-to-action section with navigation buttons."""
    st.markdown("---")
    st.markdown("### 🚀 Ready to Get Started?")
    
    cta_col1, cta_col2, cta_col3 = st.columns([2, 2, 1])
    
    with cta_col1:
        if st.button(
            "📤 Start Your First RFP",
            type="primary",
            use_container_width=True,
            help="Upload an RFP to begin processing"
        ):
            st.switch_page("pages/1_📤_Upload_RFP.py")
    
    with cta_col2:
        if st.button(
            "📚 See Example RFP",
            use_container_width=True,
            help="Load a demo RFP to explore features"
        ):
            # Import here to avoid circular dependency
            from src.components.quick_stats import load_demo_rfp
            
            load_demo_rfp()
            st.success("✅ Demo RFP loaded! Check Quick Stats below.")
            st.rerun()

