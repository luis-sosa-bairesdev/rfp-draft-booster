"""True floating chat widget for Streamlit - WhatsApp/Intercom style."""

import streamlit as st
import streamlit.components.v1 as components


def render_floating_chat_widget():
    """
    Renders a truly floating chat widget using Streamlit components + HTML/CSS.
    Button: bottom-right corner, fixed position
    Modal: Opens inline when chat state is active
    """
    
    # Initialize chat state
    if "floating_chat_open" not in st.session_state:
        st.session_state.floating_chat_open = False
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Hi there! 👋\nHow can I help you today?"}
        ]
    
    # Inject CSS for floating button and modal
    st.markdown("""
    <style>
    /* Floating Chat Button - Bottom Right */
    .stButton > button[kind="secondary"] {
        position: fixed !important;
        bottom: 20px !important;
        right: 20px !important;
        z-index: 9999 !important;
        width: 60px !important;
        height: 60px !important;
        border-radius: 50% !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
        border: none !important;
        padding: 0 !important;
        min-width: 60px !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        transform: scale(1.1) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6) !important;
    }
    
    /* Hide button text, show only emoji */
    .stButton > button[kind="secondary"] div {
        font-size: 28px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Floating button (using Streamlit button with special styling)
    # Place it in a container that's always at the bottom
    button_container = st.container()
    with button_container:
        if st.button("💬", key="floating_chat_btn", type="secondary", help="Open AI Chat"):
            st.session_state.floating_chat_open = not st.session_state.floating_chat_open
            st.rerun()
    
    # Chat modal (opens as a sidebar-like component when active)
    if st.session_state.floating_chat_open:
        with st.sidebar:
            st.markdown("### 💬 AI Assistant")
            
            # Display messages
            for msg in st.session_state.chat_messages:
                if msg["role"] == "user":
                    st.markdown(f"**You:** {msg['content']}")
                else:
                    st.markdown(f"**AI:** {msg['content']}")
            
            # Input area
            user_input = st.text_input("Type your message...", key="chat_input")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Send", key="chat_send", type="primary") and user_input.strip():
                    st.session_state.chat_messages.append({"role": "user", "content": user_input})
                    # Simulate AI response
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": f"🤖 I received: '{user_input}'. (Demo response)"
                    })
                    st.rerun()
            
            with col2:
                if st.button("Close", key="chat_close"):
                    st.session_state.floating_chat_open = False
                    st.rerun()


