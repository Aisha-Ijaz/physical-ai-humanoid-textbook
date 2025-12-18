from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
import logging

from slowapi import Limiter
from slowapi.util import get_remote_address

from src.models.api_models import AskFromSelectionRequest, AskResponse, ErrorResponse
from src.services.rag_service import RAGService
from src.utils.security import verify_api_key, validate_input_security
from src.utils.logging import logger
from src.config import settings

# Initialize limiter for this module
limiter = Limiter(key_func=get_remote_address)

router = APIRouter()

# Validation function for selected text
def validate_selected_text_input(question: str, selected_text: str) -> None:
    """
    Validate the input for selected text questions with security checks
    """
    # Apply security validation to both question and selected text
    question = validate_input_security(question)
    selected_text = validate_input_security(selected_text)

    if not question or not question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty"
        )

    if len(question.strip()) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question must be at least 3 characters long"
        )

    if len(question) > 1000:  # Max 1000 characters
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question must be less than 1000 characters"
        )

    if not selected_text or not selected_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selected text cannot be empty"
        )

    if len(selected_text) > 5000:  # Max 5000 characters
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selected text must be less than 5000 characters"
        )


@router.post("/", response_model=AskResponse, responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}, 429: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
@limiter.limit("100/minute")  # Standard users: 100 requests per minute
async def ask_from_selection(
    request: AskFromSelectionRequest,
    api_key: bool = Depends(verify_api_key)
):
    """
    Ask a question about selected text within the book.

    This endpoint processes a question specifically about user-selected text
    and returns an answer based on that selected text and related context,
    with citations and confidence score.
    """
    logger.info(f"Received ask-from-selection request: {request.question[:50]}...")

    try:
        # Validate input
        validate_selected_text_input(request.question, request.selected_text)

        # Initialize the RAG service
        rag_service = RAGService()

        # Process the question using the RAG service with selected text
        result = rag_service.ask(
            question=request.question,
            selected_text=request.selected_text,
            session_id=request.session_id
        )

        # Create the response
        response = AskResponse(
            id=result["id"],
            answer=result["answer"],
            confidence_score=result["confidence_score"],
            source_citations=result["source_citations"],
            created_at=result["created_at"]
        )

        logger.info(f"Successfully processed ask-from-selection request, confidence: {result['confidence_score']}")
        return response

    except HTTPException:
        # Re-raise HTTP exceptions as they are
        raise
    except Exception as e:
        logger.error(f"Error processing ask-from-selection request: {str(e)}", exc_info=True)

        # Determine the type of error and provide appropriate response
        error_message = str(e).lower()
        if "qdrant" in error_message or "connection" in error_message or "timeout" in error_message:
            detail_msg = "The vector database is temporarily unavailable. Please try again later."
        elif "api" in error_message or "cohere" in error_message or "authentication" in error_message:
            detail_msg = "The language model service is currently unavailable. Please check your API configuration."
        else:
            detail_msg = "An error occurred while processing your request."

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail_msg
        )


