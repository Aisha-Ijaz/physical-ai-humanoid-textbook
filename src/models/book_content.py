from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class BookContentBase(BaseModel):
    title: str
    content: str
    metadata: Optional[Dict[str, Any]] = None


class BookContentCreate(BookContentBase):
    pass


class BookContent(BookContentBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True