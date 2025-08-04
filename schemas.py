from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from models import SourceStatusEnum

class SourceBase(BaseModel):
    name: str
    url: str
    max_items: int = 10
    status: SourceStatusEnum = SourceStatusEnum.ACTIVE

class SourceCreate(SourceBase):
    pass

class SourceUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    max_items: Optional[int] = None
    status: Optional[SourceStatusEnum] = None

class SourceOut(SourceBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

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

    model_config = {"from_attributes": True}