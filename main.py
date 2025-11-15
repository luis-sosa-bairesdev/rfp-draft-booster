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
    
    # Progress Dashboard (if RFP exists)
    if rfp:
        render_progress_dashboard(requirements=requirements, risks=risks)
        st.divider()
    
    # Welcome message
    st.markdown("""
    ## Welcome!
    
    RFP Draft Booster automates the time-consuming process of responding to Request for Proposals. 
    
    ### How it works:
    
    1. **📤 Upload** - Upload your RFP PDF (up to 50MB)
    2. **🔍 Extract** - AI extracts requirements automatically
    3. **⚠️ Analyze** - Detect risky clauses and terms
    4. **🤝 Match** - Match requirements to our services
    5. **📝 Generate** - Create editable proposal draft
    6. **📄 Export** - Export to Google Docs
    
    ### Benefits:
    
    - ⚡ **80% faster** response time
    - 📈 **25-30% higher** win rates
    - 💰 **100+ hours** saved per month
    - 🎯 **Zero requirements** missed
    
    ---
    
    ### Ready to get started?
    
    Use the sidebar to navigate to **Upload RFP** to begin!
    """)
    
    # Statistics (mock data for now)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="RFPs Processed",
            value="0",
            delta="Start now!"
        )
    
    with col2:
        st.metric(
            label="Avg Response Time",
            value="N/A",
            delta="Coming soon"
        )
    
    with col3:
        st.metric(
            label="Time Saved",
            value="0 hours",
            delta="Track savings"
        )
    
    with col4:
        st.metric(
            label="Win Rate",
            value="N/A",
            delta="Measure success"
        )
    
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

