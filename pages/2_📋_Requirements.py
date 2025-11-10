"""Requirements Page - Coming in Epic 3."""

import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.session import init_session_state

st.set_page_config(
    page_title="Requirements",
    page_icon="📋",
    layout="wide"
)

init_session_state()

st.title("📋 Requirements Extraction")
st.markdown("*Coming soon in Epic 3*")

st.info("""
**This feature is under development** (Epic 3: LLM Requirement Extraction)

Once implemented, this page will:
- 🤖 Extract requirements using AI
- 📊 Categorize by type (technical, functional, timeline, budget, compliance)
- 🎯 Assign confidence scores
- ✏️ Allow manual editing and verification
- 📝 Track requirement status
""")

if st.session_state.get("current_rfp"):
    rfp = st.session_state.current_rfp
    st.success(f"✅ Current RFP: **{rfp.title}**")
    st.info(f"📄 {rfp.total_pages} pages | {len(rfp.extracted_text.split())} words")
else:
    st.warning("⚠️ No RFP uploaded yet. Please upload an RFP first.")
    if st.button("📤 Go to Upload"):
        st.switch_page("pages/1_📤_Upload_RFP.py")

