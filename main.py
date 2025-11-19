"""RFP Draft Booster - Main Streamlit Application.

This is the main entry point for the RFP Draft Booster application.
It provides the home page and navigation to other pages.
"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import settings
from utils.logging_config import setup_logging
from utils.session import init_session_state, get_current_rfp
from components.ai_assistant import render_ai_assistant_button, render_ai_assistant_modal
from components.progress_dashboard import render_progress_dashboard
from components.global_search import render_global_search
from components.quick_stats import render_quick_stats


# Page configuration
st.set_page_config(
    page_title=settings.app_name,
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/bairesdev/rfp-draft-booster',
        'Report a bug': 'https://github.com/bairesdev/rfp-draft-booster/issues',
        'About': f'# {settings.app_name}\n\nVersion {settings.version}\n\nAI-powered RFP response automation'
    }
)

# Initialize
setup_logging()
init_session_state()
# show_ai_assistant is now initialized in init_session_state()


def main() -> None:
    """Main application entry point."""
    
    # Render AI Assistant modal FIRST if open (so it's visible at top)
    if st.session_state.get("show_ai_assistant", False):
        render_ai_assistant_modal(key_suffix="main", page_context="main")
        st.markdown("---")
    
    # Header with AI Assistant button
    col1, col2 = st.columns([5, 1])
    with col1:
        st.title("🚀 RFP Draft Booster")
        st.markdown("**Accelerate your RFP responses by 80%**")
    with col2:
        render_ai_assistant_button(key_suffix="main")
    
    st.divider()
    
    # Global Search
    rfp = get_current_rfp()
    requirements = st.session_state.get("requirements", [])
    risks = st.session_state.get("risks", [])
    
    with st.expander("🔍 Global Search", expanded=False):
        render_global_search(rfp=rfp, requirements=requirements, risks=risks)
    
    st.divider()
    
    # Welcome message
    st.markdown("""
    ## Welcome to RFP Draft Booster! 👋
    
    Automate your RFP response process and **save 80% of your time**.
    
    ### 🚀 Quick Start
    
    1. **📤 Upload** your RFP PDF
    2. **🔍 Extract** requirements automatically  
    3. **⚠️ Analyze** risks and red flags
    4. **🤝 Match** with your services
    5. **✍️ Generate** proposal draft
    6. **📄 Export** to DOCX
    
    ### 💰 Business Impact
    
    - ⚡ **80% faster** response time
    - 📈 **Higher win rates** with better proposals
    - 💵 **Significant cost savings** on proposal teams
    - 🎯 **Zero requirements** missed
    
    ---
    """)
    
    # CTA Buttons
    cta_col1, cta_col2, cta_col3 = st.columns([2, 2, 1])
    
    with cta_col1:
        if st.button(
            "📤 Upload Your First RFP",
            type="primary",
            use_container_width=True,
            help="Start by uploading an RFP document"
        ):
            st.switch_page("pages/1_📤_Upload_RFP.py")
    
    with cta_col2:
        if st.button(
            "💰 Calculate Your ROI",
            use_container_width=True,
            help="Estimate time and cost savings"
        ):
            st.switch_page("pages/7_💰_ROI_Calculator.py")
    
    st.markdown("---")
    
    # Quick Stats (NEW - Epic 8)
    render_quick_stats()
    
    # Progress Dashboard (if RFP exists)
    if rfp:
        st.markdown("---")
        st.subheader("📈 Progress Dashboard")
        render_progress_dashboard(requirements=requirements, risks=risks)
    
    st.divider()
    
    # Footer
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>Built with ❤️ by BairesDev | Powered by AI</p>
        <p style='font-size: 0.9em;'>Version {version}</p>
    </div>
    """.format(version=settings.version), unsafe_allow_html=True)


if __name__ == "__main__":
    main()

