from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import logging
import os
import tempfile
from pathlib import Path
from data_extractor import extractor
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from transformers import pipeline

# Import knowledge base components
try:
    from haystack_config import knowledge_base
    from document_processor import document_processor
    HAYSTACK_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Haystack not available: {e}")
    HAYSTACK_AVAILABLE = False

app = FastAPI(
    title="AIxMultimodal API",
    description="Backend API for AIxMultimodal application with Knowledge Base",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3002",
        "http://127.0.0.1:3002"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class Message(BaseModel):
    id: Optional[int] = None
    content: str
    sender: str
    timestamp: Optional[str] = None

class User(BaseModel):
    id: Optional[int] = None
    username: str
    email: str

class SearchQuery(BaseModel):
    query: str
    top_k: Optional[int] = 5

# In-memory storage (replace with database in production)
messages: List[Message] = []
users: List[User] = []

# NLP pipelines (summarization, entity extraction)
summarizer = pipeline('summarization', model='facebook/bart-large-cnn')
ner = pipeline('ner', grouped_entities=True)

def analyze_document(text):
    summary = summarizer(text, max_length=100, min_length=30, do_sample=False)[0]['summary_text']
    entities = [ent['word'] for ent in ner(text)]
    return summary, entities

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to AIxMultimodal API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AIxMultimodal API"}

@app.get("/api/messages")
async def get_messages():
    """Get all messages"""
    return {"messages": messages}

@app.post("/api/messages")
async def create_message(message: Message):
    """Create a new message"""
    message.id = len(messages) + 1
    messages.append(message)
    return {"message": "Message created successfully", "data": message}

@app.get("/api/users")
async def get_users():
    """Get all users"""
    return {"users": users}

@app.post("/api/users")
async def create_user(user: User):
    """Create a new user"""
    # Check if user already exists
    for existing_user in users:
        if existing_user.email == user.email:
            raise HTTPException(status_code=400, detail="User with this email already exists")
    
    user.id = len(users) + 1
    users.append(user)
    return {"message": "User created successfully", "data": user}

@app.get("/api/users/{user_id}")
async def get_user(user_id: int):
    """Get a specific user by ID"""
    for user in users:
        if user.id == user_id:
            return {"user": user}
    raise HTTPException(status_code=404, detail="User not found")

# Knowledge Base Endpoints
@app.post("/api/knowledge-base/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and index a document in the knowledge base"""
    if not HAYSTACK_AVAILABLE:
        raise HTTPException(status_code=503, detail="Knowledge base service not available")
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Validate file
        validation = document_processor.validate_file(file.filename, len(file_content))
        if not validation["valid"]:
            raise HTTPException(status_code=400, detail=validation["message"])
        
        # Process document
        documents = document_processor.process_uploaded_file(
            file_content, file.filename, file.content_type
        )
        
        # Add to knowledge base
        result = knowledge_base.add_documents(documents)
        
        if result["success"]:
            return {
                "message": "Document uploaded and indexed successfully",
                "filename": file.filename,
                "document_count": result["document_count"],
                "total_documents": knowledge_base.get_document_count()
            }
        else:
            raise HTTPException(status_code=500, detail=result["message"])
            
    except Exception as e:
        logging.error(f"❌ Failed to upload document {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

@app.post("/api/knowledge-base/search")
async def search_documents(search_query: SearchQuery):
    """Search documents in the knowledge base"""
    if not HAYSTACK_AVAILABLE:
        raise HTTPException(status_code=503, detail="Knowledge base service not available")
    
    try:
        result = knowledge_base.search_documents(search_query.query, search_query.top_k)
        
        if result["success"]:
            return {
                "message": "Search completed successfully",
                "query": result["query"],
                "documents": result["documents"],
                "total_results": result["total_results"]
            }
        else:
            raise HTTPException(status_code=500, detail=result["message"])
            
    except Exception as e:
        logging.error(f"❌ Failed to search documents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search documents: {str(e)}")

@app.get("/api/knowledge-base/status")
async def get_knowledge_base_status():
    """Get knowledge base status and statistics"""
    if not HAYSTACK_AVAILABLE:
        return {
            "available": False,
            "message": "Knowledge base service not available"
        }
    
    try:
        document_count = knowledge_base.get_document_count()
        return {
            "available": True,
            "document_count": document_count,
            "message": "Knowledge base is operational"
        }
    except Exception as e:
        logging.error(f"❌ Failed to get knowledge base status: {e}")
        return {
            "available": False,
            "message": f"Knowledge base error: {str(e)}"
        }

@app.delete("/api/knowledge-base/clear")
async def clear_knowledge_base():
    """Clear all documents from the knowledge base"""
    if not HAYSTACK_AVAILABLE:
        raise HTTPException(status_code=503, detail="Knowledge base service not available")
    
    try:
        result = knowledge_base.clear_documents()
        
        if result["success"]:
            return {"message": "Knowledge base cleared successfully"}
        else:
            raise HTTPException(status_code=500, detail=result["message"])
            
    except Exception as e:
        logging.error(f"❌ Failed to clear knowledge base: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear knowledge base: {str(e)}")

# Data Extraction endpoints
@app.post("/api/extract/upload")
async def upload_for_extraction(file: UploadFile = File(...)):
    """Upload a PDF file for data extraction."""
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported for extraction")
        
        # Create temporary directory for extraction
        temp_dir = Path(tempfile.mkdtemp())
        file_path = temp_dir / file.filename
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Store file path in session (in production, use proper session management)
        # For now, we'll use a simple approach
        extraction_files = getattr(app.state, 'extraction_files', {})
        file_id = f"extract_{len(extraction_files) + 1}"
        extraction_files[file_id] = str(file_path)
        app.state.extraction_files = extraction_files
        
        return {
            "success": True,
            "file_id": file_id,
            "filename": file.filename,
            "message": "File uploaded successfully for extraction"
        }
        
    except Exception as e:
        logging.error(f"Error uploading file for extraction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/api/extract/process")
async def process_extraction(file_id: str = Form(...)):
    """Process data extraction from uploaded PDF."""
    try:
        # Get file path from session
        extraction_files = getattr(app.state, 'extraction_files', {})
        if file_id not in extraction_files:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_path = extraction_files[file_id]
        
        # Create output directory
        output_dir = Path(tempfile.mkdtemp())
        output_path = output_dir / f"extracted_{Path(file_path).stem}.xlsx"
        
        # Process extraction
        result = extractor.extract_and_convert(file_path, str(output_path))
        
        if result["success"]:
            # Store output path for download
            extraction_outputs = getattr(app.state, 'extraction_outputs', {})
            extraction_outputs[file_id] = str(output_path)
            app.state.extraction_outputs = extraction_outputs
            
            return {
                "success": True,
                "file_id": file_id,
                "excel_file": str(output_path),
                "summary": result["summary"],
                "message": "Extraction completed successfully"
            }
        else:
            raise HTTPException(status_code=500, detail=f"Extraction failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        logging.error(f"Error processing extraction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.get("/api/extract/download/{file_id}")
async def download_extracted_excel(file_id: str):
    """Download the extracted Excel file."""
    try:
        extraction_outputs = getattr(app.state, 'extraction_outputs', {})
        if file_id not in extraction_outputs:
            raise HTTPException(status_code=404, detail="Extracted file not found")
        
        excel_path = extraction_outputs[file_id]
        
        if not os.path.exists(excel_path):
            raise HTTPException(status_code=404, detail="Excel file not found")
        
        return FileResponse(
            path=excel_path,
            filename=f"extracted_data_{file_id}.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        logging.error(f"Error downloading extracted file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@app.get("/api/extract/status/{file_id}")
async def get_extraction_status(file_id: str):
    """Get the status of an extraction process."""
    try:
        extraction_files = getattr(app.state, 'extraction_files', {})
        extraction_outputs = getattr(app.state, 'extraction_outputs', {})
        
        if file_id not in extraction_files:
            raise HTTPException(status_code=404, detail="File not found")
        
        has_output = file_id in extraction_outputs
        
        return {
            "file_id": file_id,
            "uploaded": True,
            "processed": has_output,
            "download_available": has_output
        }
        
    except Exception as e:
        logging.error(f"Error getting extraction status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

@app.post("/api/analysis/matrix")
async def create_document_matrix(files: list[UploadFile] = File(...)):
    """Upload multiple reports, analyze, and return a document matrix and clusters."""
    docs = []
    filenames = []
    for file in files:
        content = await file.read()
        text = content.decode(errors='ignore')
        summary, entities = analyze_document(text)
        docs.append({'filename': file.filename, 'text': text, 'summary': summary, 'entities': ', '.join(entities)})
        filenames.append(file.filename)
    # Create DataFrame
    df = pd.DataFrame(docs)
    # TF-IDF for clustering
    tfidf = TfidfVectorizer(stop_words='english')
    X = tfidf.fit_transform(df['summary'])
    kmeans = KMeans(n_clusters=min(3, len(df)), random_state=42).fit(X)
    df['cluster'] = kmeans.labels_
    # Return as JSON
    return {
        'matrix': df.to_dict(orient='records'),
        'columns': list(df.columns),
        'clusters': df.groupby('cluster')['filename'].apply(list).to_dict()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001) 