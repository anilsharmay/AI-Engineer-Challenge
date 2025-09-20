# Import required FastAPI components for building the API
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
# Import Pydantic for data validation and settings management
from pydantic import BaseModel
# Import OpenAI client for interacting with OpenAI's API
from openai import OpenAI
import os
import asyncio
import pickle
import shutil
from typing import Optional, List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

# Import aimakerspace components for RAG functionality
import sys
sys.path.append(str(Path(__file__).parent.parent))
from aimakerspace.vectordatabase import VectorDatabase
from aimakerspace.text_utils import PDFLoader, CharacterTextSplitter
from aimakerspace.openai_utils.embedding import EmbeddingModel
from aimakerspace.openai_utils.chatmodel import ChatOpenAI

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

# Get paths for uploads and vector stores
uploads_path = Path(__file__).parent / "uploads"
vector_stores_path = Path(__file__).parent / "vector_stores"

# Create directories if they don't exist
uploads_path.mkdir(exist_ok=True)
vector_stores_path.mkdir(exist_ok=True)

# Mount static files for the frontend (only if directory exists)
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

# Global storage for document status
document_status: Dict[str, Dict[str, Any]] = {}

# Helper function to clear all documents for single PDF workflow
async def clear_all_documents():
    """Clear all existing PDF files and vector databases for single PDF workflow."""
    try:
        # Clear all PDF files in uploads directory
        for file_path in uploads_path.glob("*.pdf"):
            if file_path.is_file():
                file_path.unlink()
        
        # Clear all vector database files
        for file_path in vector_stores_path.glob("*.pkl"):
            if file_path.is_file():
                file_path.unlink()
        
        # Clear document status tracking
        document_status.clear()
        
    except Exception as e:
        print(f"Warning: Error clearing documents: {str(e)}")

# Define the data models for chat requests using Pydantic
# This ensures incoming request data is properly validated
class ChatRequest(BaseModel):
    developer_message: str  # Message from the developer/system
    user_message: str      # Message from the user
    model: Optional[str] = None  # Optional model selection
    api_key: Optional[str] = None  # Optional API key (can use env var)

class RAGChatRequest(BaseModel):
    user_message: str      # Message from the user
    model: Optional[str] = None  # Optional model selection
    api_key: Optional[str] = None  # Optional API key (can use env var)

class DocumentStatus(BaseModel):
    filename: str
    status: str  # "uploaded", "processing", "indexed", "error"
    chunks_count: Optional[int] = None
    error_message: Optional[str] = None

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

# PDF Upload endpoint
@app.post("/api/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF file for processing and indexing. Replaces any existing PDF."""
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Validate file size (10MB limit)
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=400, detail="File size must be less than 10MB")
        
        # Clear all existing documents and vector databases (single PDF workflow)
        await clear_all_documents()
        
        # Save file
        file_path = uploads_path / file.filename
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        # Update document status (only one document at a time)
        document_status.clear()  # Clear all previous documents
        document_status[file.filename] = {
            "filename": file.filename,
            "status": "uploaded",
            "chunks_count": None,
            "error_message": None
        }
        
        return {
            "message": f"PDF '{file.filename}' uploaded successfully (replaced previous document)",
            "filename": file.filename,
            "size": file_size
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# PDF Processing endpoint
@app.post("/api/process-pdf/{filename}")
async def process_pdf(filename: str):
    """Process and index a PDF file for RAG functionality."""
    try:
        # Check if file exists
        file_path = uploads_path / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        # Update status to processing
        if filename in document_status:
            document_status[filename]["status"] = "processing"
        
        # Load PDF and extract text
        pdf_loader = PDFLoader(str(file_path))
        documents = pdf_loader.load_documents()
        
        if not documents or not documents[0].strip():
            raise HTTPException(status_code=400, detail="No text content found in PDF")
        
        # Split text into chunks
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_texts(documents)
        
        # Create vector database
        vector_db = VectorDatabase()
        await vector_db.abuild_from_list(chunks)
        
        # Save vector database (only the vectors, not the full object)
        vector_db_path = vector_stores_path / f"{filename}.pkl"
        with open(vector_db_path, "wb") as f:
            # Save only the vectors dictionary, not the full VectorDatabase object
            pickle.dump(vector_db.vectors, f)
        
        # Update document status
        if filename in document_status:
            document_status[filename].update({
                "status": "indexed",
                "chunks_count": len(chunks)
            })
        
        return {
            "message": f"PDF '{filename}' processed and indexed successfully",
            "filename": filename,
            "chunks_count": len(chunks)
        }
        
    except Exception as e:
        # Update status to error
        if filename in document_status:
            document_status[filename].update({
                "status": "error",
                "error_message": str(e)
            })
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

# RAG Chat endpoint
@app.post("/api/rag-chat")
async def rag_chat(request: RAGChatRequest):
    """Chat with the current document using RAG (single document workflow)."""
    try:
        # Check if there's any indexed document (single document workflow)
        indexed_docs = [doc for doc in document_status.values() if doc["status"] == "indexed"]
        
        if not indexed_docs:
            raise HTTPException(status_code=400, detail="No document is currently loaded. Please upload a PDF first.")
        
        # Get the single active document
        active_doc = indexed_docs[0]
        document_name = active_doc["filename"]
        
        # Load vector database
        vector_db_path = vector_stores_path / f"{document_name}.pkl"
        if not vector_db_path.exists():
            raise HTTPException(status_code=404, detail="Vector database not found")
        
        with open(vector_db_path, "rb") as f:
            vectors_dict = pickle.load(f)
        
        # Recreate vector database from saved vectors
        vector_db = VectorDatabase()
        vector_db.vectors = vectors_dict
        
        # Retrieve relevant context
        relevant_chunks = vector_db.search_by_text(
            query_text=request.user_message,
            k=5,
            return_as_text=True
        )
        
        if not relevant_chunks:
            raise HTTPException(status_code=400, detail="No relevant context found")
        
        # Create RAG prompt
        context = "\n\n".join(relevant_chunks)
        rag_prompt = f"""You are a helpful assistant that answers questions based ONLY on the provided context from a PDF document. 
Do not use any external knowledge. If the answer is not in the context, clearly state that the information is not available in the document.

Context from document:
{context}

Question: {request.user_message}

Answer based only on the context above:"""
        
        # Get API key and model
        api_key = request.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=400, detail="OpenAI API key is required")
        
        model = request.model or os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
        
        # Initialize chat model
        chat_model = ChatOpenAI(model_name=model)
        
        # Create streaming response
        async def generate():
            try:
                async for chunk in chat_model.astream([{"role": "user", "content": rag_prompt}]):
                    yield chunk
            except Exception as e:
                yield f"Error: {str(e)}"
        
        return StreamingResponse(generate(), media_type="text/plain")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Document management endpoints
@app.get("/api/documents")
async def list_documents():
    """List all uploaded documents and their status."""
    return {"documents": list(document_status.values())}

@app.get("/api/documents/{filename}")
async def get_document_status(filename: str):
    """Get the status of a specific document."""
    if filename not in document_status:
        raise HTTPException(status_code=404, detail="Document not found")
    return document_status[filename]

@app.delete("/api/documents/{filename}")
async def delete_document(filename: str):
    """Delete a document and its vector store."""
    try:
        # Remove PDF file
        file_path = uploads_path / filename
        if file_path.exists():
            file_path.unlink()
        
        # Remove vector store
        vector_db_path = vector_stores_path / f"{filename}.pkl"
        if vector_db_path.exists():
            vector_db_path.unlink()
        
        # Remove from status tracking
        if filename in document_status:
            del document_status[filename]
        
        return {"message": f"Document '{filename}' deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")

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