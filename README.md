

## <h1 align="center" id="heading"> AI Engineer Challenge </h1>


## 🖥️ MS DOS Chatbot - Retro AI Experience

Experience the future of AI with the aesthetic of the past! Our MS DOS-style chatbot brings together the best of both worlds:

### ✨ Features
- **Authentic DOS Interface**: Blue background (#000080), white text, Courier font
- **Nostalgic Command Prompts**: Messages appear as `C:\You>` and `C:\Assistant>`
- **Clean Borderless Design**: No white borders - authentic DOS command line feel
- **Real-time AI Responses**: Powered by OpenAI's GPT models
- **Keyboard Shortcuts**: `Enter` to send, `Ctrl+C` to clear (just like DOS!)
- **Environment Configuration**: Secure API key storage with `.env` files
- **Vercel Deployment Ready**: Works both locally and in production

### 🚀 Quick Start

#### **Local Development:**
1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/AI-Engineer-Challenge.git
   cd AI-Engineer-Challenge
   ```

2. **Set up environment variables**:
   ```bash
   cd api
   # Edit .env file with your OpenAI API key
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the server**:
   ```bash
   python3 vercel_app.py
   ```

5. **Open your browser**: Navigate to `http://localhost:8000`

#### **Vercel Deployment:**
1. **Connect your repository** to Vercel
2. **Set environment variables** in Vercel dashboard:
   - `OPENAI_API_KEY` - Your OpenAI API key
   - `DEFAULT_MODEL` - (optional) Default model (gpt-4o-mini)
3. **Deploy automatically** - Vercel will build and deploy your chatbot!

### 🎮 Try It Now
The chatbot is ready to use! Experience the most retro-tastic AI chat interface around.

### 🎯 Perfect For
- **Nostalgia Lovers**: Relive the DOS era with modern AI
- **Developers**: Technical discussions in a familiar interface
- **Retro Computing Fans**: The best of both worlds
- **Anyone Who Misses the 80s**: Because sometimes you just need that blue screen!

### 🏗️ Technical Implementation

#### **Architecture:**
- **Backend**: FastAPI with OpenAI integration
- **Frontend**: Embedded HTML/CSS/JavaScript with DOS styling
- **Deployment**: Vercel serverless functions
- **Environment**: Secure `.env` configuration

#### **Key Features:**
- **Nostalgic Prompts**: `C:\You>` and `C:\Assistant>` command line style
- **Borderless Design**: Clean, authentic DOS interface
- **Real-time AI**: Streaming responses from OpenAI GPT models
- **Environment Security**: API keys stored in environment variables
- **Cross-platform**: Works on any modern browser

#### **File Structure:**
```
AI-Engineer-Challenge/
├── api/
│   ├── vercel_app.py      # Main FastAPI application
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Environment variables (create this)
├── frontend/              # Static files (embedded in vercel_app.py)
├── vercel.json            # Vercel deployment configuration
└── README.md              # This file
```

#### **Environment Variables:**
```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
DEFAULT_MODEL=gpt-4o-mini
HOST=0.0.0.0
PORT=8000
```
---

This was implemented as part of the application process to be accepted into the AI Engineering Bootcamp by AI Makerspace. 