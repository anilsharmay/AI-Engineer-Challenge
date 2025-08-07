# Minimal Vercel serverless function for MS DOS Chatbot
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI application
app = FastAPI(title="MS DOS Chatbot API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the data model for chat requests
class ChatRequest(BaseModel):
    developer_message: str
    user_message: str
    model: Optional[str] = None
    api_key: Optional[str] = None

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "MS DOS Chatbot API is running"}

# Simple chat endpoint (non-streaming for now)
@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        # Get API key from request or environment
        api_key = request.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=400, detail="OpenAI API key is required.")
        
        # For now, return a simple response to test the endpoint
        return {"response": f"Received: {request.user_message}", "status": "success"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve the main page
@app.get("/")
async def read_root():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MS DOS Chatbot</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                background-color: #000080;
                font-family: 'Courier New', monospace;
                color: #ffffff;
                height: 100vh;
                display: flex;
                flex-direction: column;
            }

            .dos-header {
                background-color: #000080;
                color: #ffffff;
                padding: 10px;
                border-bottom: 2px solid #ffffff;
                font-weight: bold;
            }

            .dos-window {
                flex: 1;
                background-color: #000080;
                margin: 10px;
                border: 2px solid #ffffff;
                display: flex;
                flex-direction: column;
            }

            .chat-container {
                flex: 1;
                padding: 20px;
                overflow-y: auto;
                background-color: #000080;
            }

            .message {
                margin-bottom: 15px;
                padding: 10px;
                border: 1px solid #ffffff;
                background-color: #000080;
            }

            .user-message {
                border-left: 4px solid #00ff00;
            }

            .assistant-message {
                border-left: 4px solid #ffff00;
            }

            .message-header {
                font-weight: bold;
                margin-bottom: 5px;
                color: #00ff00;
            }

            .assistant-message .message-header {
                color: #ffff00;
            }

            .message-content {
                color: #ffffff;
                white-space: pre-wrap;
            }

            .input-container {
                padding: 20px;
                background-color: #000080;
                border-top: 2px solid #ffffff;
            }

            .input-line {
                display: flex;
                align-items: center;
                gap: 10px;
            }

            .prompt {
                color: #00ff00;
                font-weight: bold;
            }

            .chat-input {
                flex: 1;
                background-color: #000080;
                border: none;
                color: #ffffff;
                font-family: 'Courier New', monospace;
                font-size: 16px;
                outline: none;
            }

            .chat-input::placeholder {
                color: #808080;
            }

            .typing-indicator {
                color: #ffff00;
                font-style: italic;
                margin-top: 10px;
                display: none;
            }

            .error-message {
                color: #ff0000;
                margin-top: 10px;
            }

            .status-bar {
                background-color: #000080;
                color: #ffffff;
                padding: 5px 10px;
                border-top: 1px solid #ffffff;
                font-size: 12px;
            }
        </style>
    </head>
    <body>
        <div class="dos-header">
            MS DOS Chatbot v1.0 - Press Enter to send message
        </div>
        
        <div class="dos-window">
            <div class="chat-container" id="chatContainer">
                <div class="message assistant-message">
                    <div class="message-header">ASSISTANT.EXE</div>
                    <div class="message-content">Welcome to the MS DOS Chatbot! I'm ready to help you with any questions. Type your message and press Enter to start chatting.</div>
                </div>
            </div>
            
            <div class="input-container">
                <div class="input-line">
                    <span class="prompt">C:\CHAT\></span>
                    <input type="text" id="chatInput" class="chat-input" placeholder="Type your message here..." autocomplete="off">
                </div>
                <div class="typing-indicator" id="typingIndicator">
                    ASSISTANT.EXE is processing...
                </div>
                <div class="error-message" id="errorMessage"></div>
            </div>
        </div>
        
        <div class="status-bar">
            Ready | Press Enter to send | Ctrl+C to clear
        </div>

        <script>
            class DOSChatbot {
                constructor() {
                    this.chatInput = document.getElementById('chatInput');
                    this.chatContainer = document.getElementById('chatContainer');
                    this.typingIndicator = document.getElementById('typingIndicator');
                    this.errorMessage = document.getElementById('errorMessage');
                    
                    this.setupEventListeners();
                    this.focusInput();
                }

                setupEventListeners() {
                    this.chatInput.addEventListener('keypress', (e) => {
                        if (e.key === 'Enter') {
                            this.sendMessage();
                        }
                    });

                    document.addEventListener('keydown', (e) => {
                        if (e.ctrlKey && e.key === 'c') {
                            e.preventDefault();
                            this.clearChat();
                        }
                    });

                    document.addEventListener('click', () => {
                        this.focusInput();
                    });
                }

                focusInput() {
                    this.chatInput.focus();
                }

                async sendMessage() {
                    const message = this.chatInput.value.trim();
                    if (!message) return;

                    this.addMessage('USER.EXE', message, 'user');
                    this.chatInput.value = '';
                    this.showTypingIndicator();

                    try {
                        const response = await this.callAPI(message);
                        this.hideTypingIndicator();
                        this.addMessage('ASSISTANT.EXE', response, 'assistant');
                    } catch (error) {
                        this.hideTypingIndicator();
                        this.showError(`Error: ${error.message}`);
                    }
                }

                async callAPI(message) {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            developer_message: "You are a helpful assistant in a MS DOS-style interface. Keep responses concise and technical, as if you're running in a DOS environment.",
                            user_message: message
                        })
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }

                    const data = await response.json();
                    return data.response || 'No response received';
                }

                addMessage(sender, content, type) {
                    const messageDiv = document.createElement('div');
                    messageDiv.className = `message ${type}-message`;
                    
                    const headerDiv = document.createElement('div');
                    headerDiv.className = 'message-header';
                    headerDiv.textContent = sender;
                    
                    const contentDiv = document.createElement('div');
                    contentDiv.className = 'message-content';
                    contentDiv.textContent = content;
                    
                    messageDiv.appendChild(headerDiv);
                    messageDiv.appendChild(contentDiv);
                    
                    this.chatContainer.appendChild(messageDiv);
                    this.scrollToBottom();
                }

                showTypingIndicator() {
                    this.typingIndicator.style.display = 'block';
                    this.scrollToBottom();
                }

                hideTypingIndicator() {
                    this.typingIndicator.style.display = 'none';
                }

                showError(message) {
                    this.errorMessage.textContent = message;
                    this.errorMessage.style.display = 'block';
                    setTimeout(() => {
                        this.errorMessage.style.display = 'none';
                    }, 5000);
                }

                clearChat() {
                    this.chatContainer.innerHTML = `
                        <div class="message assistant-message">
                            <div class="message-header">ASSISTANT.EXE</div>
                            <div class="message-content">Chat cleared. Ready for new conversation.</div>
                        </div>
                    `;
                    this.hideTypingIndicator();
                    this.errorMessage.style.display = 'none';
                }

                scrollToBottom() {
                    this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
                }
            }

            document.addEventListener('DOMContentLoaded', () => {
                new DOSChatbot();
            });
        </script>
    </body>
    </html>
    """)

# For local development
if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host=host, port=port)
