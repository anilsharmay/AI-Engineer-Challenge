# 🖥️ MS DOS Chatbot API

Welcome to the backend API for the most retro-tastic chatbot around! This FastAPI-powered service brings the DOS aesthetic to modern AI conversations.

## 🚀 Quick Start

### 1. Environment Setup

Create a `.env` file in the `api` directory:

```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Model Configuration
DEFAULT_MODEL=gpt-4o-mini

# Optional: Server Configuration
HOST=0.0.0.0
PORT=8000
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Server

```bash
python3 app.py
```

The server will start on `http://localhost:8000`

## 🔧 API Endpoints

### POST `/api/chat`
Main chat endpoint that handles streaming responses.

**Request Body:**
```json
{
  "developer_message": "System prompt for the AI",
  "user_message": "User's message",
  "model": "gpt-4o-mini",  // Optional
  "api_key": "sk-..."      // Optional (uses .env if not provided)
}
```

**Response:** Streaming text response

### GET `/api/health`
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "message": "MS DOS Chatbot API is running"
}
```

### GET `/`
Serves the MS DOS chatbot frontend.

## 🎨 Features

- **Environment Configuration**: Uses `.env` file for secure API key storage
- **Streaming Responses**: Real-time AI responses for authentic DOS feel
- **CORS Enabled**: Works with any frontend
- **Error Handling**: Graceful error responses with helpful messages
- **Static File Serving**: Serves the frontend directly

## 🔐 Security

- API keys are loaded from environment variables
- No hardcoded secrets in the code
- CORS configured for development (customize for production)

## 🛠️ Configuration Options

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `OPENAI_API_KEY` | Required | Your OpenAI API key |
| `DEFAULT_MODEL` | `gpt-4o-mini` | Default AI model to use |
| `HOST` | `0.0.0.0` | Server host address |
| `PORT` | `8000` | Server port |

## 🎯 Perfect For

- **Retro Computing Fans**: DOS aesthetic with modern AI
- **Developers**: Clean API with streaming support
- **AI Enthusiasts**: Easy integration with OpenAI models
- **Nostalgia Lovers**: The best of both worlds!

---

*"In a world of modern APIs, be the DOS interface that stands out!"* 🖥️✨ 