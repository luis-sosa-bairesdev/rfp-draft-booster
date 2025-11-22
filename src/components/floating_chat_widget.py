"""True floating chat widget for Streamlit - WhatsApp/Intercom style."""

import streamlit as st


def render_floating_chat_widget():
    """
    Renders a truly floating chat widget using custom HTML/CSS.
    Button: bottom-right corner, fixed position
    Modal: Slides up when clicked
    """
    
    # Initialize chat state
    if "floating_chat_open" not in st.session_state:
        st.session_state.floating_chat_open = False
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    
    # Inject custom HTML/CSS for floating chat
    st.markdown("""
    <style>
    /* Floating Chat Button - Bottom Right */
    .floating-chat-button {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 9999;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
        border: none;
    }
    
    .floating-chat-button:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    .floating-chat-button svg {
        width: 28px;
        height: 28px;
        fill: white;
    }
    
    /* Chat Modal - Slides up from button */
    .chat-modal {
        position: fixed;
        bottom: 90px;
        right: 20px;
        width: 380px;
        height: 600px;
        background: white;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        z-index: 9998;
        display: none;
        flex-direction: column;
        overflow: hidden;
        animation: slideUp 0.3s ease-out;
    }
    
    .chat-modal.active {
        display: flex;
    }
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Chat Header */
    .chat-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .chat-header h3 {
        margin: 0;
        font-size: 18px;
        font-weight: 600;
    }
    
    .chat-close {
        background: none;
        border: none;
        color: white;
        font-size: 24px;
        cursor: pointer;
        padding: 0;
        width: 30px;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        transition: background 0.2s;
    }
    
    .chat-close:hover {
        background: rgba(255, 255, 255, 0.2);
    }
    
    /* Chat Body */
    .chat-body {
        flex: 1;
        padding: 16px;
        overflow-y: auto;
        background: #f8f9fa;
    }
    
    .chat-message {
        margin-bottom: 12px;
        padding: 10px 14px;
        border-radius: 12px;
        max-width: 80%;
        word-wrap: break-word;
    }
    
    .chat-message.user {
        background: #667eea;
        color: white;
        margin-left: auto;
        text-align: right;
    }
    
    .chat-message.assistant {
        background: white;
        color: #333;
        margin-right: auto;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Chat Input */
    .chat-input-area {
        padding: 16px;
        background: white;
        border-top: 1px solid #e0e0e0;
    }
    
    /* Notification Badge */
    .chat-badge {
        position: absolute;
        top: -5px;
        right: -5px;
        background: #ef4444;
        color: white;
        border-radius: 50%;
        width: 22px;
        height: 22px;
        font-size: 12px;
        font-weight: bold;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    </style>
    
    <!-- Floating Chat Button -->
    <button class="floating-chat-button" onclick="toggleChat()" id="chatButton">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
        </svg>
        <span class="chat-badge" id="chatBadge" style="display: none;">1</span>
    </button>
    
    <!-- Chat Modal -->
    <div class="chat-modal" id="chatModal">
        <div class="chat-header">
            <h3>💬 AI Assistant</h3>
            <button class="chat-close" onclick="toggleChat()">✕</button>
        </div>
        <div class="chat-body" id="chatBody">
            <div class="chat-message assistant">
                Hi there! 👋<br>
                How can I help you today?
            </div>
        </div>
        <div class="chat-input-area">
            <div style="display: flex; gap: 8px;">
                <input 
                    type="text" 
                    placeholder="Write your message..." 
                    id="chatInput"
                    style="flex: 1; padding: 10px; border: 1px solid #e0e0e0; border-radius: 8px; font-size: 14px;"
                    onkeypress="if(event.key === 'Enter') sendMessage()"
                />
                <button 
                    onclick="sendMessage()"
                    style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: 600;"
                >
                    Send
                </button>
            </div>
        </div>
    </div>
    
    <script>
    function toggleChat() {
        const modal = document.getElementById('chatModal');
        const badge = document.getElementById('chatBadge');
        modal.classList.toggle('active');
        badge.style.display = 'none';
    }
    
    function sendMessage() {
        const input = document.getElementById('chatInput');
        const message = input.value.trim();
        if (!message) return;
        
        const chatBody = document.getElementById('chatBody');
        
        // Add user message
        const userMsg = document.createElement('div');
        userMsg.className = 'chat-message user';
        userMsg.textContent = message;
        chatBody.appendChild(userMsg);
        
        // Clear input
        input.value = '';
        
        // Scroll to bottom
        chatBody.scrollTop = chatBody.scrollHeight;
        
        // Simulate AI response (you can connect to real AI here via Streamlit callback)
        setTimeout(() => {
            const aiMsg = document.createElement('div');
            aiMsg.className = 'chat-message assistant';
            aiMsg.textContent = '🤖 I received your message: "' + message + '". This is a demo response. Connect to AI for real answers!';
            chatBody.appendChild(aiMsg);
            chatBody.scrollTop = chatBody.scrollHeight;
        }, 1000);
    }
    </script>
    """, unsafe_allow_html=True)

