"""True floating chat widget for Streamlit - WhatsApp/Intercom style."""

import streamlit as st
import streamlit.components.v1 as components


def render_floating_chat_widget():
    """
    Renders a truly floating chat widget using HTML iframe component.
    Button: bottom-right corner, fixed position
    Modal: Opens as overlay above button
    """
    
    # HTML + CSS + JavaScript in an iframe (bypass React restrictions)
    html_code = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {
                margin: 0;
                padding: 0;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            }
            
            /* Floating Button - Bottom Right */
            .chat-button {
                position: fixed;
                bottom: 20px;
                right: 20px;
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border: none;
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 28px;
                color: white;
                transition: all 0.3s ease;
                z-index: 9999;
            }
            
            .chat-button:hover {
                transform: scale(1.1);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
            }
            
            /* Chat Modal - Appears above button */
            .chat-modal {
                position: fixed;
                bottom: 90px;
                right: 20px;
                width: 380px;
                height: 550px;
                background: white;
                border-radius: 16px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                display: none;
                flex-direction: column;
                overflow: hidden;
                z-index: 9998;
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
            
            /* Header */
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
            
            .close-btn {
                background: none;
                border: none;
                color: white;
                font-size: 24px;
                cursor: pointer;
                width: 30px;
                height: 30px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
                transition: background 0.2s;
            }
            
            .close-btn:hover {
                background: rgba(255, 255, 255, 0.2);
            }
            
            /* Messages Area */
            .chat-messages {
                flex: 1;
                padding: 16px;
                overflow-y: auto;
                background: #f8f9fa;
            }
            
            .message {
                margin-bottom: 12px;
                padding: 10px 14px;
                border-radius: 12px;
                max-width: 80%;
                word-wrap: break-word;
            }
            
            .message.assistant {
                background: white;
                color: #333;
                margin-right: auto;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            
            .message.user {
                background: #667eea;
                color: white;
                margin-left: auto;
                text-align: right;
            }
            
            /* Input Area */
            .chat-input {
                padding: 16px;
                background: white;
                border-top: 1px solid #e0e0e0;
                display: flex;
                gap: 8px;
            }
            
            .chat-input input {
                flex: 1;
                padding: 10px;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                outline: none;
            }
            
            .chat-input input:focus {
                border-color: #667eea;
            }
            
            .chat-input button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 600;
                transition: opacity 0.2s;
            }
            
            .chat-input button:hover {
                opacity: 0.9;
            }
        </style>
    </head>
    <body>
        <!-- Floating Button -->
        <button class="chat-button" onclick="toggleChat()">
            💬
        </button>
        
        <!-- Chat Modal -->
        <div class="chat-modal" id="chatModal">
            <div class="chat-header">
                <h3>💬 AI Assistant</h3>
                <button class="close-btn" onclick="toggleChat()">✕</button>
            </div>
            
            <div class="chat-messages" id="messages">
                <div class="message assistant">
                    Hi there! 👋<br>How can I help you today?
                </div>
            </div>
            
            <div class="chat-input">
                <input 
                    type="text" 
                    id="messageInput" 
                    placeholder="Write your message..."
                    onkeypress="if(event.key==='Enter') sendMessage()"
                />
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>
        
        <script>
            function toggleChat() {
                const modal = document.getElementById('chatModal');
                modal.classList.toggle('active');
            }
            
            function sendMessage() {
                const input = document.getElementById('messageInput');
                const messages = document.getElementById('messages');
                const text = input.value.trim();
                
                if (!text) return;
                
                // Add user message
                const userMsg = document.createElement('div');
                userMsg.className = 'message user';
                userMsg.textContent = text;
                messages.appendChild(userMsg);
                
                // Clear input
                input.value = '';
                
                // Scroll to bottom
                messages.scrollTop = messages.scrollHeight;
                
                // Simulate AI response
                setTimeout(() => {
                    const aiMsg = document.createElement('div');
                    aiMsg.className = 'message assistant';
                    aiMsg.innerHTML = '🤖 I received: "' + text + '"<br>This is a demo response!';
                    messages.appendChild(aiMsg);
                    messages.scrollTop = messages.scrollHeight;
                }, 800);
            }
        </script>
    </body>
    </html>
    """
    
    # Render as HTML component (height 0 since it's fixed position)
    components.html(html_code, height=0, scrolling=False)


