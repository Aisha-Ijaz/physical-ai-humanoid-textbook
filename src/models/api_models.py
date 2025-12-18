from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from .question import Answer


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    session_id: Optional[str] = None


class AskFromSelectionRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    selected_text: str = Field(min_length=1, max_length=5000)
    session_id: Optional[str] = None


class AskResponse(BaseModel):
    id: str
    answer: str
    confidence_score: float = Field(ge=0.0, le=1.0)  # Confidence score between 0.0 and 1.0
    source_citations: List[dict]
    created_at: datetime


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[str] = None


class ErrorResponse(BaseModel):
    error: ErrorDetail