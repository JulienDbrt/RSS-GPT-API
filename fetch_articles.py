import feedparser
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Source, Article
from datetime import datetime
from llm_summarizer import summarize_article
import os

DEFAULT_LANGUAGE = os.environ.get("SUMMARY_LANGUAGE", "en")

def fetch_and_store_articles():
    db: Session = SessionLocal()
    sources = db.query(Source).filter(Source.status == "active").all()
    for source in sources:
        print(f"Fetching: {source.name} ({source.url})")
        feed = feedparser.parse(source.url)
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
            article = Article(
                source_id=source.id,
                title=getattr(entry, "title", "Untitled"),
                url=getattr(entry, "link", ""),
                published_at=parse_datetime(getattr(entry, "published", None)),
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

def parse_datetime(dt_str):
    if not dt_str:
        return None
    try:
        return datetime(*feedparser._parse_date(dt_str)[:6])
    except Exception:
        return None

if __name__ == "__main__":
    fetch_and_store_articles()