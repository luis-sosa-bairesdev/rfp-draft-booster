"""
Floating Chat Component - WhatsApp/Intercom style chat widget.

This component provides a floating chat button in the bottom-left corner
that opens a modal chat interface when clicked.
"""

import streamlit as st
from typing import Optional
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.ai_assistant import AIAssistant, AIMessage
from utils.session import get_current_rfp


def open_floating_chat():
    """Open the floating chat modal."""
    st.session_state.show_floating_chat = True


def close_floating_chat():
    """Close the floating chat modal."""
    st.session_state.show_floating_chat = False


def render_floating_chat_button():
    """
    Render a floating chat button in the bottom-left corner.
    Uses custom CSS to position it fixed on the page.
    """
    # Initialize chat state
    if "show_floating_chat" not in st.session_state:
        st.session_state.show_floating_chat = False
    
    # Floating button CSS
    st.markdown("""
    <style>
    .floating-chat-btn {
        position: fixed;
        bottom: 20px;
        left: 20px;
        z-index: 1000;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        font-size: 28px;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .floating-chat-btn:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    .floating-chat-btn:active {
        transform: scale(0.95);
    }
    
    /* Chat notification badge */
    .chat-badge {
        position: absolute;
        top: -5px;
        right: -5px;
        background: #ef4444;
        color: white;
        border-radius: 50%;
        width: 20px;
        height: 20px;
        font-size: 12px;
        font-weight: bold;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Check if chat is already open
    chat_open = st.session_state.get("floating_chat_open", False)
    
    # Render button using Streamlit's native button (positioned with CSS)
    # We use a container with custom class for positioning
    button_container = st.container()
    
    with button_container:
        # Use columns to position button
        col1, col2, col3 = st.columns([1, 10, 1])
        with col1:
            if not chat_open:
                if st.button("💬", key="floating_chat_toggle", 
                            help="Open AI Assistant Chat",
                            use_container_width=False):
                    st.session_state.floating_chat_open = True
                    st.rerun()


def render_floating_chat_modal():
    """
    Render the floating chat modal when open.
    Displays as a card-style modal in the bottom-left corner.
    """
    if not st.session_state.get("floating_chat_open", False):
        return
    
    # Modal CSS
    st.markdown("""
    <style>
    .floating-chat-modal {
        position: fixed;
        bottom: 90px;
        left: 20px;
        width: 380px;
        max-height: 600px;
        background: white;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
        z-index: 999;
        display: flex;
        flex-direction: column;
        animation: slideUp 0.3s ease;
    }
    
    @keyframes slideUp {
        from {
            transform: translateY(20px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    .chat-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 16px;
        border-radius: 16px 16px 0 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .chat-body {
        flex: 1;
        overflow-y: auto;
        padding: 16px;
        max-height: 450px;
    }
    
    .chat-message {
        margin-bottom: 12px;
        padding: 10px 14px;
        border-radius: 12px;
        max-width: 85%;
        word-wrap: break-word;
    }
    
    .chat-message.user {
        background: #667eea;
        color: white;
        margin-left: auto;
        text-align: right;
    }
    
    .chat-message.assistant {
        background: #f3f4f6;
        color: #1f2937;
        margin-right: auto;
    }
    
    .chat-timestamp {
        font-size: 0.75rem;
        opacity: 0.7;
        margin-top: 4px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create modal container
    with st.container():
        # Header
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown("### 💬 AI Assistant")
        with col2:
            if st.button("✕", key="close_floating_chat", 
                        help="Close chat",
                        use_container_width=True):
                st.session_state.floating_chat_open = False
                st.rerun()
        
        st.divider()
        
        # Initialize assistant
        if "ai_assistant" not in st.session_state:
            from services.llm_client import create_llm_client
            llm_client = create_llm_client(fallback=True)
            st.session_state.ai_assistant = AIAssistant(llm_client=llm_client, temperature=0.7)
        
        assistant = st.session_state.ai_assistant
        
        # Get context
        rfp = get_current_rfp()
        requirements = st.session_state.get("requirements", [])
        risks = st.session_state.get("risks", [])
        
        # Display conversation history
        history = assistant.get_history()
        
        if history:
            st.markdown("#### 💬 Conversation")
            chat_container = st.container()
            with chat_container:
                for i, msg in enumerate(history[-10:]):  # Last 10 messages
                    role_icon = "👤" if msg.role == "user" else "🤖"
                    role_name = "You" if msg.role == "user" else "AI Assistant"
                    
                    with st.chat_message(msg.role):
                        st.markdown(f"**{role_icon} {role_name}**")
                        st.markdown(msg.content)
                        if msg.timestamp:
                            st.caption(msg.timestamp.strftime("%I:%M %p"))
        else:
            st.info("👋 **Hi! I'm your AI Assistant.**\n\n"
                   "I can help you with:\n"
                   "- Understanding your RFP\n"
                   "- Analyzing requirements\n"
                   "- Identifying risks\n"
                   "- Drafting responses\n\n"
                   "Ask me anything!")
        
        # Input area
        st.divider()
        
        # Quick action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 Summarize RFP", key="quick_summarize", 
                        use_container_width=True,
                        disabled=not rfp):
                if rfp:
                    question = "Can you provide a brief summary of this RFP?"
                    _handle_chat_message(assistant, question, rfp, requirements, risks)
        
        with col2:
            if st.button("⚠️ Key Risks", key="quick_risks",
                        use_container_width=True,
                        disabled=not risks):
                if risks:
                    question = "What are the most critical risks I should be aware of?"
                    _handle_chat_message(assistant, question, rfp, requirements, risks)
        
        # Chat input
        with st.form(key="chat_input_form", clear_on_submit=True):
            user_question = st.text_area(
                "Type your message...",
                height=80,
                placeholder="Ask me anything about your RFP...",
                label_visibility="collapsed",
                key="chat_input_text"
            )
            
            col1, col2 = st.columns([3, 1])
            with col2:
                send_btn = st.form_submit_button(
                    "Send 📤",
                    use_container_width=True,
                    type="primary"
                )
            
            if send_btn and user_question.strip():
                _handle_chat_message(assistant, user_question.strip(), rfp, requirements, risks)


def _handle_chat_message(
    assistant: AIAssistant,
    question: str,
    rfp: Optional[any],
    requirements: list,
    risks: list
):
    """Handle sending and receiving chat messages."""
    with st.spinner("🤖 Thinking..."):
        try:
            response = assistant.ask(
                question=question,
                rfp=rfp,
                requirements=requirements,
                risks=risks
            )
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")


def init_floating_chat():
    """
    Initialize floating chat state.
    Call this in your page initialization.
    """
    if "floating_chat_open" not in st.session_state:
        st.session_state.floating_chat_open = False


def render_floating_chat():
    """
    Main function to render the complete floating chat widget.
    Call this once at the end of your page, after all other content.
    """
    init_floating_chat()
    render_floating_chat_button()
    render_floating_chat_modal()

