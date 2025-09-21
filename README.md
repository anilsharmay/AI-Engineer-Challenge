## <h1 align="center" id="heading"> AI Engineer Challenge </h1>

## 🖥️ DOSGPT - Retro AI with Modern RAG Capabilities

Experience the future of AI with the aesthetic of the past! DOSGPT combines nostalgic MS DOS styling with cutting-edge Retrieval-Augmented Generation (RAG) technology, bringing together the best of both worlds.

### ✨ Features

#### **🎮 Dual-Mode Interface**
- **General Mode**: Traditional AI chat with OpenAI GPT models
- **RAG Mode**: Upload PDF documents and chat with their contents using advanced RAG technology
- **Seamless Mode Switching**: Toggle between modes with separate chat histories

#### **📄 Advanced PDF Processing**
- **Single PDF Workflow**: Upload one PDF at a time for focused document analysis
- **Automatic Document Processing**: PDFs are automatically parsed, chunked, and indexed
- **Vector Database**: OpenAI embeddings with cosine similarity for efficient document retrieval
- **Smart Document Management**: Upload new PDFs automatically replace previous ones

#### **⌨️ Authentic DOS Experience**
- **Nostalgic Interface**: Blue background (#000080), white text, Courier font
- **Command Prompts**: Messages appear as `C:\CHAT\>` and `C:\RAG\>`
- **Keyboard Shortcuts**: 
  - `Enter` to send messages
  - `Ctrl+C` to clear chat
  - `F1` to upload PDF (RAG mode)
  - `F3` to delete current PDF (RAG mode)
- **Borderless Design**: Clean, authentic DOS command line feel

#### **🔧 Technical Excellence**
- **Environment-Aware Deployment**: Works seamlessly on both local development and Vercel production
- **Secure Configuration**: API keys stored in environment variables
- **Real-time Streaming**: Live AI responses with streaming technology
- **Cross-platform Compatibility**: Works on any modern browser

### 🚀 Quick Start

#### **Local Development:**

1. **Clone the repository**:
   ```bash
   git clone https://github.com/anilsharmay/AI-Engineer-Challenge.git
   cd AI-Engineer-Challenge
   ```

2. **Set up environment variables**:
   ```bash
   cd api
   # Create .env file with your OpenAI API key
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the server**:
   ```bash
   python3 app.py
   ```

5. **Open your browser**: Navigate to `http://localhost:8000`

#### **Vercel Deployment:**

1. **Connect your repository** to Vercel
2. **Set environment variables** in Vercel dashboard:
   - `OPENAI_API_KEY` - Your OpenAI API key
   - `DEFAULT_MODEL` - (optional) Default model (gpt-4o-mini)
3. **Deploy automatically** - Vercel will build and deploy DOSGPT!

### 🎯 How to Use

#### **General Mode:**
- Click "General Mode" or press `Enter` to start chatting
- Ask any questions and get AI-powered responses
- Perfect for general conversations and assistance

#### **RAG Mode:**
- Click "RAG Mode" to switch to document analysis
- Press `F1` or use the upload button to select a PDF
- Once uploaded, ask questions about the document content
- Press `F3` to delete the current document and upload a new one

### 🎮 Try It Now
DOSGPT is ready to use! Experience the most retro-tastic AI chat interface with modern RAG capabilities.

### 🎯 Perfect For
- **Document Analysis**: Upload PDFs and get intelligent answers about their content
- **Nostalgia Lovers**: Relive the DOS era with modern AI
- **Developers**: Technical discussions in a familiar interface
- **Researchers**: Analyze documents with AI-powered insights
- **Retro Computing Fans**: The best of both worlds

### 🏗️ Technical Implementation

#### **Architecture:**
- **Backend**: FastAPI with OpenAI integration and custom RAG pipeline
- **Frontend**: Complete HTML/CSS/JavaScript with DOS styling and dual-mode functionality
- **RAG System**: Custom `aimakerspace` modules for PDF processing and vector storage
- **Deployment**: Vercel serverless functions with environment-aware file paths
- **Environment**: Secure `.env` configuration

#### **Key Features:**
- **Dual-Mode Interface**: Separate General and RAG chat experiences
- **PDF Processing**: Automatic text extraction, chunking, and OpenAI embedding generation
- **Vector Database**: OpenAI embeddings with cosine similarity for document retrieval
- **Single PDF Workflow**: Focused document analysis with automatic replacement
- **Environment Detection**: Automatic local vs. Vercel path configuration
- **Real-time Streaming**: Live AI responses with proper message handling
- **Separate Chat Histories**: Independent conversation tracking per mode

#### **File Structure:**
```
AI-Engineer-Challenge/
├── api/
│   ├── app.py              # Main FastAPI application (Vercel-compatible)
│   ├── index.py            # Simple index file
│   ├── requirements.txt    # Python dependencies (includes RAG libraries)
│   └── .env                # Environment variables (create this)
├── aimakerspace/           # Custom RAG modules
│   ├── __init__.py
│   ├── openai_utils/       # OpenAI integration utilities
│   │   ├── chatmodel.py    # Chat model wrapper
│   │   ├── embedding.py    # Embedding utilities
│   │   └── prompts.py      # Prompt templates
│   ├── text_utils.py       # PDF processing utilities
│   └── vectordatabase.py   # Vector database implementation
├── frontend/
│   └── index.html          # Complete DOSGPT frontend with RAG functionality
├── docs/
│   └── GIT_SETUP.md        # Git setup documentation
├── vercel.json             # Vercel deployment configuration
├── pyproject.toml          # Python project configuration
├── runtime.txt             # Python runtime specification
└── README.md               # This file
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

#### **API Endpoints:**
- `GET /` - Serve the DOSGPT frontend
- `POST /api/chat` - General AI chat
- `POST /api/upload-pdf` - Upload PDF for RAG processing
- `POST /api/process-pdf/{filename}` - Process uploaded PDF
- `POST /api/rag-chat` - Chat with document using RAG
- `GET /api/documents` - Get document status
- `DELETE /api/documents/{filename}` - Delete document
- `GET /api/health` - Health check

### 🔧 Development Notes

#### **RAG Implementation:**
- Uses custom `aimakerspace` modules for PDF processing
- Implements OpenAI embeddings with cosine similarity search
- Uses `text-embedding-3-small` model for vector generation
- Supports automatic text chunking with configurable overlap
- Handles single PDF workflow with automatic document replacement

#### **Deployment:**
- Environment-aware file paths (local vs. Vercel `/tmp` directories)
- Unified `app.py` file works for both local and production
- Automatic dependency management for RAG libraries
- Vercel serverless function optimization

---

This was implemented as part of the application process to be accepted into the AI Engineering Bootcamp by AI Makerspace.