from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID, uuid4


class QuestionBase(BaseModel):
    content: str
    selected_text: Optional[str] = None
    session_id: Optional[str] = None


class QuestionCreate(QuestionBase):
    pass


class Question(QuestionBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class SourceCitation(BaseModel):
    section: str
    page: Optional[int] = None
    text: str


class AnswerBase(BaseModel):
    content: str
    confidence_score: float
    source_citations: List[SourceCitation]


class AnswerCreate(AnswerBase):
    question_id: str


class Answer(AnswerBase):
    id: str
    question_id: str
    created_at: datetime

    class Config:
        from_attributes = True