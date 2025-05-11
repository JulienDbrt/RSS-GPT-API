import feedparser
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Source, Article
from datetime import datetime
from llm_summarizer import summarize_article
from config import DEFAULT_LANGUAGE
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_and_store_articles():
    db: Session = SessionLocal()
    sources = db.query(Source).filter(Source.status == "active").all()
    for source in sources:
        print(f"Fetching: {source.name} ({source.url})")
        feed = feedparser.parse(source.url)
        if getattr(feed, "bozo", False):
            logger.warning(f"Feedparser bozo error for {source.url}: {getattr(feed, 'bozo_exception', None)}")
        for entry in feed.entries[:source.max_items]:
            # Check for duplicate by URL
            exists = db.query(Article).filter(Article.url == entry.link).first()
            if exists:
                continue
            content = getattr(entry, "summary", None)
            # Summarize and extract keywords using OpenAI
            summary, keywords = summarize_article(
                content or "",
                language=DEFAULT_LANGUAGE
            )
            if summary is None or keywords is None:
                logger.warning(f"Summarization failed for article: {getattr(entry, 'title', 'Untitled')} ({getattr(entry, 'link', '')})")
            article = Article(
                source_id=source.id,
                title=getattr(entry, "title", "Untitled"),
                url=getattr(entry, "link", ""),
                published_at=parse_datetime(getattr(entry, "published", None), entry=entry),
                content=content,
                summary=summary,
                keywords=keywords,
                language=DEFAULT_LANGUAGE,
                created_at=datetime.utcnow()
            )
            db.add(article)
        db.commit()
    db.close()
    print("Done.")

from dateutil import parser as date_parser

def parse_datetime(dt_str, entry=None):
    """
    Parse a datetime string from an RSS entry.
    Prefer entry.published_parsed if available, else use dateutil.parser.
    """
    if entry and hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            return datetime(*entry.published_parsed[:6])
        except Exception as e:
            logger.warning(f"Failed to parse published_parsed: {e}")
    if not dt_str:
        return None
    try:
        return date_parser.parse(dt_str)
    except Exception as e:
        logger.error(f"Error parsing datetime from '{dt_str}': {e}", exc_info=True)
        return None

if __name__ == "__main__":
    fetch_and_store_articles()