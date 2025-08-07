# Alternative Vercel entry point
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
from typing import Optional
from pathlib import Path
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

# Get the path to frontend files
frontend_path = Path(__file__).parent.parent / "frontend"

# Mount static files for the frontend (only if directory exists)
if frontend_path.exists():
    from fastapi.staticfiles import StaticFiles
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

# Define the data model for chat requests
class ChatRequest(BaseModel):
    developer_message: str
    user_message: str
    model: Optional[str] = None
    api_key: Optional[str] = None

# Define the main chat endpoint
@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        # Get API key from request or environment
        api_key = request.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=400, detail="OpenAI API key is required.")
        
        # Get model from request or environment
        model = request.model or os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
        
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Create streaming response
        async def generate():
            stream = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": request.developer_message},
                    {"role": "user", "content": request.user_message}
                ],
                stream=True,
                max_tokens=1000,
                temperature=0.7
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        return StreamingResponse(generate(), media_type="text/plain")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "MS DOS Chatbot API is running"}

# Serve the main page
@app.get("/")
async def read_root():
    index_path = frontend_path / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    else:
        return HTMLResponse("""
        <html>
            <head><title>MS DOS Chatbot</title></head>
            <body>
                <h1>MS DOS Chatbot</h1>
                <p>Frontend files not found. Please check the deployment.</p>
                <p>API is running at <a href="/api/health">/api/health</a></p>
            </body>
        </html>
        """)

# For local development
if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host=host, port=port)
