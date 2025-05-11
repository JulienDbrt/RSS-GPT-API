from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime

from database import get_db
from models import Article
from schemas import ArticleOut

router = APIRouter(prefix="/articles", tags=["articles"])

@router.get("/", response_model=List[ArticleOut])
def list_articles(
    db: Session = Depends(get_db),
    source_id: Optional[int] = None,
    day: Optional[date] = Query(None, description="Filter by publication date (YYYY-MM-DD)")
):
    query = db.query(Article)
    if source_id:
        query = query.filter(Article.source_id == source_id)
    if day:
        start = datetime.combine(day, datetime.min.time())
        end = datetime.combine(day, datetime.max.time())
        query = query.filter(Article.published_at >= start, Article.published_at <= end)
    return query.order_by(Article.published_at.desc()).all()