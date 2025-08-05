# worker.py
import asyncio
import logging
from datetime import datetime

import feedparser
import openai
from arq import create_pool
from arq.connections import RedisSettings
from dateutil.parser import parse as parse_date
from sqlalchemy import select

from config import settings
from database import SessionLocal
from models import Article, Source, SourceStatusEnum

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
openai.api_key = settings.OPENAI_API_KEY
client = openai.AsyncOpenAI()

async def get_summary_and_keywords(ctx, content: str) -> tuple[str | None, str | None]:
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
            model=settings.OPENAI_MODEL, messages=[{"role": "user", "content": prompt}], temperature=0.2, timeout=90.0
        )
        raw_text = response.choices[0].message.content
        summary = raw_text.split("SUMMARY:")[1].split("KEYWORDS:")[0].strip()
        keywords = raw_text.split("KEYWORDS:")[1].strip()
        return summary, keywords
    except Exception as e:
        logging.error(f"OpenAI API call failed for job {ctx.get('job_id', 'N/A')}: {e}")
        return None, None

async def process_article(ctx, article_entry: dict, source_id: int):
    """Tâche atomique pour traiter UN SEUL article."""
    db = SessionLocal()
    try:
        article_url = article_entry['link']
        stmt = select(Article.id).where(Article.url == article_url).limit(1)
        if db.execute(stmt).first():
            return

        content = (article_entry.get('content', [{}])[0].get('value') or article_entry.get('summary', ''))
        summary, keywords = await get_summary_and_keywords(ctx, content)
        if not summary or not keywords:
            logging.warning(f"Could not generate summary/keywords for: {article_entry['title']}")
            return

        new_article = Article(
            source_id=source_id, title=article_entry['title'], url=article_url,
            published_at=parse_date(article_entry['published']) if 'published' in article_entry else datetime.utcnow(),
            content=content, summary=summary, keywords=keywords, language=settings.SUMMARY_LANGUAGE
        )
        db.add(new_article)
        db.commit()
        logging.info(f"-> Article processed and saved: {article_entry['title']}")
    except Exception as e:
        logging.error(f"Failed to process article {article_entry.get('link', 'N/A')}: {e}")
        db.rollback()
    finally:
        db.close()

async def fetch_source(ctx, source_id: int):
    """Tâche qui fetch UN SEUL flux RSS et enfile des tâches `process_article`."""
    db = SessionLocal()
    try:
        source = db.query(Source).filter(Source.id == source_id).first()
        if not source: return

        logging.info(f"Fetching source: {source.name}")
        feed = await asyncio.to_thread(feedparser.parse, source.url)
        if feed.bozo: raise ValueError(f"Feed parsing error for {source.url}")

        for entry in feed.entries[:source.max_items]:
            await ctx['arq_pool'].enqueue_job('process_article', entry, source.id)

        source.last_fetched_at = datetime.utcnow()
        source.status = SourceStatusEnum.ACTIVE
        db.commit()
    except Exception as e:
        logging.error(f"Failed to fetch source {source_id}: {e}")
        db.rollback(); source.status = SourceStatusEnum.ERROR; db.commit()
    finally:
        db.close()

async def startup(ctx):
    ctx['arq_pool'] = await create_pool(RedisSettings(host=settings.REDIS_HOST, port=settings.REDIS_PORT))
    logging.info("Worker startup complete.")

async def shutdown(ctx):
    await ctx['arq_pool'].close()
    logging.info("Worker shutdown complete.")

class WorkerSettings:
    functions = [fetch_source, process_article, get_summary_and_keywords]
    on_startup = startup
    on_shutdown = shutdown
    max_jobs = 20
