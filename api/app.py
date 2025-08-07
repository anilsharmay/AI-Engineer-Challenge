# Import required FastAPI components for building the API
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
# Import Pydantic for data validation and settings management
from pydantic import BaseModel
# Import OpenAI client for interacting with OpenAI's API
from openai import OpenAI
import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI application with a title
app = FastAPI(title="MS DOS Chatbot API")

# Configure CORS (Cross-Origin Resource Sharing) middleware
# This allows the API to be accessed from different domains/origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any origin
    allow_credentials=True,  # Allows cookies to be included in requests
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers in requests
)

# Get the path to frontend files
frontend_path = Path(__file__).parent.parent / "frontend"

# Mount static files for the frontend (only if directory exists)
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

# Define the data model for chat requests using Pydantic
# This ensures incoming request data is properly validated
class ChatRequest(BaseModel):
    developer_message: str  # Message from the developer/system
    user_message: str      # Message from the user
    model: Optional[str] = None  # Optional model selection
    api_key: Optional[str] = None  # Optional API key (can use env var)

# Define the main chat endpoint that handles POST requests
@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        # Get API key from request or environment
        api_key = request.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=400, detail="OpenAI API key is required. Set it in .env file or provide in request.")
        
        # Get model from request or environment
        model = request.model or os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
        
        # Initialize OpenAI client with the provided API key
        client = OpenAI(api_key=api_key)
        
        # Create an async generator function for streaming responses
        async def generate():
            # Create a streaming chat completion request
            stream = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": request.developer_message},
                    {"role": "user", "content": request.user_message}
                ],
                stream=True,  # Enable streaming response
                max_tokens=1000,  # Limit response length for DOS-style brevity
                temperature=0.7  # Add some creativity while keeping it technical
            )
            
            # Yield each chunk of the response as it becomes available
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        # Return a streaming response to the client
        return StreamingResponse(generate(), media_type="text/plain")
    
    except Exception as e:
        # Handle any errors that occur during processing
        raise HTTPException(status_code=500, detail=str(e))

# Define a health check endpoint to verify API status
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

# Entry point for running the application directly
if __name__ == "__main__":
    import uvicorn
    # Get host and port from environment or use defaults
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    # Start the server on all network interfaces (0.0.0.0) on port 8000
    uvicorn.run(app, host=host, port=port)
