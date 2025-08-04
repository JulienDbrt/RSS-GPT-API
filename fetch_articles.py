import asyncio
import feedparser
import openai
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime
from dateutil.parser import parse as parse_date
import logging

from database import SessionLocal
from models import Source, Article, SourceStatusEnum
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configure OpenAI client
client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def get_summary_and_keywords(content: str) -> tuple[str | None, str | None]:
    """Asks OpenAI for a summary and keywords asynchronously."""
    if not content or len(content.strip()) < 50:
        logging.warning("Content too short to summarize, skipping.")
        return None, None

    prompt = f"""
    Analyze the following article and provide:
    1. A concise, neutral summary in {settings.SUMMARY_LANGUAGE}, approximately {settings.SUMMARY_LENGTH} words long.
    2. A list of {settings.KEYWORD_COUNT} relevant keywords, separated by commas.

    Your response MUST be in this exact format, with no other text:
    SUMMARY: [Your summary here]
    KEYWORDS: [Your keywords here]

    ARTICLE:
    {content[:8000]}
    """

    try:
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            timeout=90.0
        )
        raw_text = response.choices[0].message.content

        summary = raw_text.split("SUMMARY:")[1].split("KEYWORDS:")[0].strip()
        keywords = raw_text.split("KEYWORDS:")[1].strip()
        return summary, keywords
    except Exception as e:
        logging.error(f"OpenAI API call failed: {e}")
        return None, None

async def process_feed(source: Source, db: Session):
    """Fetches a single RSS feed, processes entries, and saves them."""
    logging.info(f"Processing source: {source.name} ({source.url})")
    try:
        feed = await asyncio.to_thread(feedparser.parse, source.url)
        if feed.bozo:
            raise ValueError(f"Feed parsing error: {getattr(feed, 'bozo_exception', 'Unknown error')}")

        source.last_fetched_at = datetime.utcnow()

        new_articles_count = 0
        for entry in feed.entries[:source.max_items]:
            article_url = entry.link

            # Check if article already exists using a more efficient query
            stmt = select(Article.id).where(Article.url == article_url).limit(1)
            if db.execute(stmt).first():
                continue

            content = ""
            if 'content' in entry and entry.content:
                content = entry.content[0].value
            if not content and 'summary' in entry:
                content = entry.summary

            summary, keywords = await get_summary_and_keywords(content)

            if not summary or not keywords:
                logging.warning(f"Could not generate summary/keywords for: {entry.title}")
                continue

            new_article = Article(
                source_id=source.id,
                title=entry.title,
                url=article_url,
                published_at=parse_date(entry.published) if 'published' in entry else datetime.utcnow(),
                content=content,
                summary=summary,
                keywords=keywords,
                language=settings.SUMMARY_LANGUAGE,
            )
            db.add(new_article)
            new_articles_count += 1

        source.status = SourceStatusEnum.ACTIVE
        db.commit()
        logging.info(f"  -> Source '{source.name}' processed. Added {new_articles_count} new articles.")

    except Exception as e:
        logging.error(f"Failed to process source {source.name}: {e}")
        source.status = SourceStatusEnum.ERROR
        db.rollback()
        db.query(Source).filter(Source.id == source.id).update({"status": SourceStatusEnum.ERROR})
        db.commit()

async def main():
    """Main function to run the fetching process."""
    logging.info("--- Starting article fetching process ---")
    db = SessionLocal()
    try:
        active_sources = db.execute(
            select(Source).where(Source.status == SourceStatusEnum.ACTIVE)
        ).scalars().all()

        tasks = [process_feed(source, db) for source in active_sources]
        await asyncio.gather(*tasks)

    finally:
        db.close()
    logging.info("--- Article fetching process finished ---")

if __name__ == "__main__":
    asyncio.run(main())
