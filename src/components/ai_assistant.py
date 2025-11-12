"""
AI Assistant Component - Reusable chat interface for Streamlit.
"""

import streamlit as st
from typing import Optional, List, Dict, Any
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.ai_assistant import AIAssistant, AIMessage
from models import RFP, Requirement, Risk
from utils.session import get_current_rfp


def init_ai_assistant() -> AIAssistant:
    """Initialize AI Assistant in session state."""
    if "ai_assistant" not in st.session_state:
        from services.llm_client import create_llm_client
        llm_client = create_llm_client(fallback=True)
        st.session_state.ai_assistant = AIAssistant(llm_client=llm_client, temperature=0.7)
    return st.session_state.ai_assistant


def render_ai_assistant_button(key_suffix: str = ""):
    """Render the purple 'Ask' button in the header.
    
    Args:
        key_suffix: Optional suffix to make button key unique per page
    """
    button_key = f"btn_ai_assistant_{key_suffix}" if key_suffix else "btn_ai_assistant"
    
    # Render button - use on_click callback for more reliable handling
    def open_ai_assistant():
        """Callback to open AI Assistant modal."""
        st.session_state.show_ai_assistant = True
        st.rerun()  # Force rerun to show modal immediately
    
    if st.button("💬 Ask", key=button_key, use_container_width=True, 
                 help="Get help about your RFP, requirements, and risks",
                 type="primary",
                 on_click=open_ai_assistant):
        # This block executes after callback, ensure state is set and rerun
        st.session_state.show_ai_assistant = True
        st.rerun()  # Force rerun to show modal immediately


def render_ai_assistant_modal(key_suffix: str = "", page_context: str = ""):
    """Render the AI Assistant modal dialog.
    
    Args:
        key_suffix: Optional suffix to make button keys unique per page
        page_context: Current page context ('upload', 'requirements', 'risks', 'draft', 'main')
    """
    if not st.session_state.get("show_ai_assistant", False):
        return
    
    # Add JavaScript to scroll to modal when it opens
    st.markdown("""
    <script>
    window.addEventListener('load', function() {
        // Scroll to top when modal opens
        if (window.location.hash !== '#ai-assistant') {
            window.scrollTo(0, 0);
        }
    });
    </script>
    """, unsafe_allow_html=True)
    
    # Add anchor for scrolling
    st.markdown('<div id="ai-assistant-modal"></div>', unsafe_allow_html=True)
    
    # Header with close button
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("### 💬 AI Assistant")
        st.caption("Ask questions about your RFP, requirements, and risks")
    with col2:
        close_key = f"btn_close_ai_assistant_{key_suffix}" if key_suffix else "btn_close_ai_assistant"
        if st.button("✕ Close", key=close_key, use_container_width=True, help="Close AI Assistant"):
            st.session_state.show_ai_assistant = False
            st.rerun()
    
    st.divider()
    
    # Initialize assistant
    assistant = init_ai_assistant()
    
    # Get context from session state
    rfp = get_current_rfp()
    requirements = st.session_state.get("requirements", [])
    risks = st.session_state.get("risks", [])
    
    # Display conversation history
    history = assistant.get_history()
    
    if history:
        st.markdown("#### 💬 Conversation History")
        for i, msg in enumerate(history[-10:]):  # Show last 10 messages
            role = msg["role"]
            content = msg["content"]
            
            if role == "user":
                with st.chat_message("user"):
                    st.write(content)
            else:
                with st.chat_message("assistant"):
                    st.write(content)
                    # Copy button
                    copy_key = f"copy_answer_{i}_{len(history)}_{key_suffix}" if key_suffix else f"copy_answer_{i}_{len(history)}"
                    if st.button("📋 Copy", key=copy_key, help="Copy answer to clipboard"):
                        st.success("✅ Copied to clipboard!")
    
    # Input area
    st.markdown("---")
    st.markdown("#### 💭 Ask a Question")
    
    input_key = f"ai_assistant_input_{key_suffix}" if key_suffix else "ai_assistant_input"
    question = st.text_input(
        "Type your question here:",
        key=input_key,
        placeholder="e.g., What are the most critical risks? How many requirements are there? Explain this requirement..."
    )
    
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        send_key = f"btn_send_question_{key_suffix}" if key_suffix else "btn_send_question"
        if st.button("📤 Send", key=send_key, use_container_width=True, type="primary"):
            if question and question.strip():
                with st.spinner("🤔 Thinking..."):
                    try:
                        response = assistant.ask(
                            question=question,
                            rfp=rfp,
                            requirements=requirements,
                            risks=risks,
                            page_context=page_context
                        )
                        # Clear input after sending
                        if input_key in st.session_state:
                            del st.session_state[input_key]
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    with col2:
        clear_key = f"btn_clear_history_{key_suffix}" if key_suffix else "btn_clear_history"
        if st.button("🗑️ Clear History", key=clear_key, use_container_width=True):
            assistant.clear_history()
            st.success("✅ Conversation history cleared!")
            st.rerun()
    
    # Context info
    st.markdown("---")
    with st.expander("ℹ️ Context Information", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Current Context:**")
            if rfp:
                st.write(f"- **RFP:** {rfp.title or rfp.file_name or 'Untitled'}")
            st.write(f"- **Requirements:** {len(requirements)}")
            st.write(f"- **Risks:** {len(risks)}")
            critical_risks = [r for r in risks if r.severity.value == "critical"]
            if critical_risks:
                st.write(f"- **Critical Risks:** {len(critical_risks)}")
        
        with col2:
            st.markdown("**Example Questions:**")
            st.write("- What are the most critical risks?")
            st.write("- How many technical requirements are there?")
            st.write("- Explain the financial risk on page 8")
            st.write("- What should I do about unacknowledged risks?")
    
    st.markdown("---")


def render_ai_assistant_in_sidebar():
    """Render AI Assistant button in sidebar (alternative placement)."""
    with st.sidebar:
        st.markdown("---")
        if st.button("💬 Ask AI Assistant", key="btn_sidebar_ai_assistant", 
                     use_container_width=True, help="Get contextual help"):
            st.session_state.show_ai_assistant = True
            st.rerun()

