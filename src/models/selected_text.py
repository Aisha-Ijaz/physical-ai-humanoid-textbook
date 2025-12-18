from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SelectedTextBase(BaseModel):
    content: str
    context_before: Optional[str] = None
    context_after: Optional[str] = None


class SelectedTextCreate(SelectedTextBase):
    pass


class SelectedText(SelectedTextBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True