from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class SourceBase(BaseModel):
    name: str
    url: str
    max_items: int = 10
    status: str = "active"

class SourceCreate(SourceBase):
    pass

class SourceUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    max_items: Optional[int] = None
    status: Optional[str] = None

class SourceOut(SourceBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
class ArticleOut(BaseModel):
    id: int
    source_id: int
    title: str
    url: str
    published_at: Optional[datetime]
    content: Optional[str]
    summary: Optional[str]
    keywords: Optional[str]
    language: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True