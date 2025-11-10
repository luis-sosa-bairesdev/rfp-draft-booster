"""Risk Analysis Page - Coming in Epic 4."""

import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.session import init_session_state

st.set_page_config(
    page_title="Risk Analysis",
    page_icon="⚠️",
    layout="wide"
)

init_session_state()

st.title("⚠️ Risk Detection & Analysis")
st.markdown("*Coming soon in Epic 4*")

st.info("""
**This feature is under development** (Epic 4: Risk Detection & Analysis)

Once implemented, this page will:
- 🔍 Detect problematic clauses automatically
- 📊 Classify by type (legal, financial, timeline, technical, compliance)
- 🎯 Assign severity (critical, high, medium, low)
- 💡 Provide mitigation recommendations
- ✏️ Suggest alternative language
- ✅ Track risk acknowledgment
""")

if st.session_state.get("current_rfp"):
    rfp = st.session_state.current_rfp
    st.success(f"✅ Current RFP: **{rfp.title}**")
    st.info(f"📄 {rfp.total_pages} pages ready for risk analysis")
else:
    st.warning("⚠️ No RFP uploaded yet. Please upload an RFP first.")
    if st.button("📤 Go to Upload"):
        st.switch_page("pages/1_📤_Upload_RFP.py")

