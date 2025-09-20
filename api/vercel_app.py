from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="DOSGPT API", version="2.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatRequest(BaseModel):
    user_message: str
    model: Optional[str] = None
    api_key: Optional[str] = None

# Serve the frontend
@app.get("/")
async def serve_frontend():
    """Serve the frontend HTML file."""
    try:
        with open("frontend/index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Frontend not found</h1>", status_code=404)

# Chat endpoint
@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        # Get API key from request or environment
        api_key = request.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            return {
                "response": "OpenAI API key is required. Please set OPENAI_API_KEY environment variable in Vercel settings.",
                "model": "error",
                "usage": {"total_tokens": 0}
            }
        
        # Get model from request or environment
        model = request.model or os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
        
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Create chat completion
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant. Respond in a helpful and informative way."},
                {"role": "user", "content": request.user_message}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        return {
            "response": response.choices[0].message.content,
            "model": model,
            "usage": response.usage.dict() if response.usage else {"total_tokens": 0}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

# Mock RAG endpoints to prevent frontend errors
@app.post("/api/upload-pdf")
async def upload_pdf():
    return {"message": "PDF upload not available in minimal version", "filename": "demo.pdf", "size": 0}

@app.post("/api/process-pdf/{filename}")
async def process_pdf(filename: str):
    return {"message": f"PDF processing not available in minimal version", "chunks_count": 0}

@app.post("/api/rag-chat")
async def rag_chat(request: ChatRequest):
    return {
        "response": "RAG functionality is not available in this minimal version. Please use General Mode for chat.",
        "model": "demo",
        "usage": {"total_tokens": 0}
    }

@app.get("/api/documents")
async def get_documents():
    return {"documents": []}

@app.delete("/api/documents/{filename}")
async def delete_document(filename: str):
    return {"message": f"Document deletion not available in minimal version"}

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "version": "2.0-minimal"}

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host=host, port=port)
