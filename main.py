import os
import sys
from pathlib import Path
import logging
from datetime import datetime
from typing import List, Optional
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Add the project root to Python path so we can import modules
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config import settings
from src.services.rag_service import RAGService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Request and Response models
class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    session_id: Optional[str] = None

class AskFromSelectionRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    selected_text: str = Field(min_length=1, max_length=5000)
    session_id: Optional[str] = None

class SourceCitation(BaseModel):
    section: str
    text: str
    page: Optional[int] = None

class AskResponse(BaseModel):
    id: str
    answer: str
    confidence_score: float = Field(ge=0.0, le=1.0)  # Confidence score between 0.0 and 1.0
    source_citations: List[SourceCitation]
    created_at: str

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[str] = None

class ErrorResponse(BaseModel):
    error: ErrorDetail

# Context manager for application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up RAG Question Answering System...")

    # Don't initialize RAG service during startup to avoid Qdrant dependency
    # RAG service will be initialized on-demand in API endpoints
    logger.info("RAG Question Answering System started (RAG service will initialize on-demand)")
    yield
    logger.info("Shutting down RAG Question Answering System...")

# Create FastAPI app instance
app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="RAG Question Answering System API for book content",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def safe_rag_call(func, *args, **kwargs):
    """Wrapper to handle RAG service calls with error handling"""
    try:
        # Initialize the RAG service
        rag_service = RAGService()
        return func(rag_service, *args, **kwargs)
    except Exception as e:
        logger.error(f"Error in RAG service: {str(e)}", exc_info=True)

        # Return an error response instead of crashing
        error_response = {
            "id": str(uuid.uuid4()),
            "answer": "We're experiencing technical difficulties. Please try again later.",
            "confidence_score": 0.0,
            "source_citations": [],
            "created_at": datetime.utcnow().isoformat()
        }
        return error_response

@app.get("/")
def read_root():
    return {"message": settings.APP_NAME, "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0", "api_prefix": settings.API_V1_STR}

# API v1 endpoints
@app.post("/v1/ask", response_model=AskResponse, responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}, 429: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def ask_full_book_v1(request: AskRequest):
    logger.info(f"Received v1 ask request: {request.question[:50]}...")

    # Call the RAG service and handle errors gracefully
    result = safe_rag_call(
        lambda svc, q, s_id: svc.ask(question=q, session_id=s_id),
        request.question,
        request.session_id
    )

    # Format the response to match the expected schema
    response = AskResponse(
        id=result["id"],
        answer=result["answer"],
        confidence_score=result["confidence_score"],
        source_citations=[
            SourceCitation(
                section=citation.get("section", "Unknown"),
                text=citation.get("text", ""),
                page=citation.get("page")
            ) for citation in result["source_citations"]
        ],
        created_at=result["created_at"]
    )

    logger.info(f"Successfully processed v1 ask request, confidence: {result['confidence_score']}")
    return response

@app.post("/v1/ask-from-selection", response_model=AskResponse, responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}, 429: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def ask_from_selection_v1(request: AskFromSelectionRequest):
    logger.info(f"Received v1 ask-from-selection request: {request.question[:50]}...")

    # Call the RAG service and handle errors gracefully
    result = safe_rag_call(
        lambda svc, q, s_text, s_id: svc.ask(question=q, selected_text=s_text, session_id=s_id),
        request.question,
        request.selected_text,
        request.session_id
    )

    # Format the response to match the expected schema
    response = AskResponse(
        id=result["id"],
        answer=result["answer"],
        confidence_score=result["confidence_score"],
        source_citations=[
            SourceCitation(
                section=citation.get("section", "Selected text"),
                text=citation.get("text", ""),
                page=citation.get("page")
            ) for citation in result["source_citations"]
        ],
        created_at=result["created_at"]
    )

    logger.info(f"Successfully processed v1 ask-from-selection request, confidence: {result['confidence_score']}")
    return response

# Legacy endpoints for frontend compatibility
@app.post("/ask", response_model=AskResponse, responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}, 429: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def ask_full_book(request: AskRequest):
    logger.info(f"Received legacy ask request: {request.question[:50]}...")

    # Call the RAG service and handle errors gracefully
    result = safe_rag_call(
        lambda svc, q, s_id: svc.ask(question=q, session_id=s_id),
        request.question,
        request.session_id
    )

    # Format the response to match the expected schema
    response = AskResponse(
        id=result["id"],
        answer=result["answer"],
        confidence_score=result["confidence_score"],
        source_citations=[
            SourceCitation(
                section=citation.get("section", "Unknown"),
                text=citation.get("text", ""),
                page=citation.get("page")
            ) for citation in result["source_citations"]
        ],
        created_at=result["created_at"]
    )

    logger.info(f"Successfully processed legacy ask request, confidence: {result['confidence_score']}")
    return response

@app.post("/ask-from-selection", response_model=AskResponse, responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}, 429: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def ask_from_selection(request: AskFromSelectionRequest):
    logger.info(f"Received legacy ask-from-selection request: {request.question[:50]}...")

    # Call the RAG service and handle errors gracefully
    result = safe_rag_call(
        lambda svc, q, s_text, s_id: svc.ask(question=q, selected_text=s_text, session_id=s_id),
        request.question,
        request.selected_text,
        request.session_id
    )

    # Format the response to match the expected schema
    response = AskResponse(
        id=result["id"],
        answer=result["answer"],
        confidence_score=result["confidence_score"],
        source_citations=[
            SourceCitation(
                section=citation.get("section", "Selected text"),
                text=citation.get("text", ""),
                page=citation.get("page")
            ) for citation in result["source_citations"]
        ],
        created_at=result["created_at"]
    )

    logger.info(f"Successfully processed legacy ask-from-selection request, confidence: {result['confidence_score']}")
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)