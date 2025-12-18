from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class ContentChunkBase(BaseModel):
    book_content_id: str
    content: str
    chunk_index: int
    embedding_id: str
    metadata: Optional[Dict[str, Any]] = None


class ContentChunkCreate(ContentChunkBase):
    pass


class ContentChunk(ContentChunkBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True