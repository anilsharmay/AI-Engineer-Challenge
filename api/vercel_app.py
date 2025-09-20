from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse, FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
import asyncio
import pickle
import shutil
from typing import Optional, List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv
import PyPDF2
import io
import re

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

# Define paths
uploads_path = Path("uploads")
vector_stores_path = Path("vector_stores")

# Create directories if they don't exist
uploads_path.mkdir(exist_ok=True)
vector_stores_path.mkdir(exist_ok=True)

# Document status tracking
document_status = {}

# Pydantic models
class ChatRequest(BaseModel):
    user_message: str
    model: Optional[str] = None
    api_key: Optional[str] = None

class RAGChatRequest(BaseModel):
    user_message: str
    model: Optional[str] = None
    api_key: Optional[str] = None

class DocumentResponse(BaseModel):
    documents: List[Dict[str, Any]]

# Simple text splitter
def split_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """Split text into chunks with overlap."""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end < len(text):
            # Try to break at sentence boundary
            for i in range(end, start + chunk_size - 100, -1):
                if text[i] in '.!?':
                    end = i + 1
                    break
        
        chunks.append(text[start:end])
        start = end - chunk_overlap
        
        if start >= len(text):
            break
    
    return chunks

# Simple keyword-based search
class SimpleVectorStore:
    def __init__(self):
        self.documents = []
    
    def add_documents(self, texts: List[str]):
        """Add documents to the store."""
        self.documents.extend(texts)
    
    def similarity_search(self, query: str, k: int = 3) -> List[str]:
        """Search for documents containing query keywords."""
        if not self.documents:
            return []
        
        # Extract keywords from query
        query_words = set(re.findall(r'\b\w+\b', query.lower()))
        
        # Score documents based on keyword matches
        scored_docs = []
        for doc in self.documents:
            doc_words = set(re.findall(r'\b\w+\b', doc.lower()))
            matches = len(query_words.intersection(doc_words))
            if matches > 0:
                scored_docs.append((matches, doc))
        
        # Sort by score and return top k
        scored_docs.sort(reverse=True)
        return [doc for _, doc in scored_docs[:k]]

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

# Upload PDF endpoint
@app.post("/api/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF file for processing and indexing."""
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        if file_size > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=400, detail="File size too large. Maximum 10MB allowed.")
        
        # Clear existing documents
        for file_path in uploads_path.glob("*.pdf"):
            if file_path.is_file():
                file_path.unlink()
        
        for file_path in vector_stores_path.glob("*.pkl"):
            if file_path.is_file():
                file_path.unlink()
        
        document_status.clear()
        
        # Save file
        file_path = uploads_path / file.filename
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        # Update document status
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

# Process PDF endpoint
@app.post("/api/process-pdf/{filename}")
async def process_pdf(filename: str):
    """Process and index a PDF file."""
    try:
        file_path = uploads_path / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Extract text from PDF
        with open(file_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="No text found in PDF")
        
        # Split text into chunks
        chunks = split_text(text)
        
        # Create vector store
        vector_store = SimpleVectorStore()
        vector_store.add_documents(chunks)
        
        # Save vector store
        vector_store_path = vector_stores_path / f"{filename}.pkl"
        with open(vector_store_path, "wb") as f:
            pickle.dump(vector_store, f)
        
        # Update document status
        document_status[filename] = {
            "filename": filename,
            "status": "indexed",
            "chunks_count": len(chunks),
            "error_message": None
        }
        
        return {
            "message": f"PDF '{filename}' processed successfully",
            "chunks_count": len(chunks)
        }
        
    except Exception as e:
        # Update document status with error
        if filename in document_status:
            document_status[filename]["status"] = "error"
            document_status[filename]["error_message"] = str(e)
        
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

# RAG chat endpoint
@app.post("/api/rag-chat")
async def rag_chat(request: RAGChatRequest):
    """Chat with the current document using RAG."""
    try:
        # Check if there's any indexed document
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
            vector_store = pickle.load(f)
        
        # Search for relevant chunks
        relevant_chunks = vector_store.similarity_search(request.user_message, k=3)
        
        if not relevant_chunks:
            raise HTTPException(status_code=400, detail="No relevant content found in document")
        
        # Create context
        context = "\n\n".join(relevant_chunks)
        
        # Get API key and model
        api_key = request.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=400, detail="OpenAI API key is required. Please set OPENAI_API_KEY environment variable in Vercel settings.")
        
        model = request.model or os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
        
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Create RAG prompt
        rag_prompt = f"""Based on the following context from the document, answer the user's question. If the answer cannot be found in the context, say so.

Context:
{context}

Question: {request.user_message}

Answer based only on the context above:"""
        
        # Create chat completion
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context. Only use information from the context."},
                {"role": "user", "content": rag_prompt}
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
        raise HTTPException(status_code=500, detail=f"RAG chat error: {str(e)}")

# Get documents endpoint
@app.get("/api/documents", response_model=DocumentResponse)
async def get_documents():
    """Get list of uploaded documents and their status."""
    return DocumentResponse(documents=list(document_status.values()))

# Delete document endpoint
@app.delete("/api/documents/{filename}")
async def delete_document(filename: str):
    """Delete a document and its vector store."""
    try:
        # Remove PDF file
        pdf_path = uploads_path / filename
        if pdf_path.exists():
            pdf_path.unlink()
        
        # Remove vector store
        vector_path = vector_stores_path / f"{filename}.pkl"
        if vector_path.exists():
            vector_path.unlink()
        
        # Remove from document status
        if filename in document_status:
            del document_status[filename]
        
        return {"message": f"Document '{filename}' deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "2.0"}

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host=host, port=port)
