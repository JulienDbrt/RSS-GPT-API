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
from config import OPENAI_MODEL, DEFAULT_LANGUAGE, DEFAULT_SUMMARY_LENGTH, DEFAULT_KEYWORD_COUNT

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ensure your OPENAI_API_KEY is set as an environment variable
# openai.api_key = os.getenv("OPENAI_API_KEY")

async def get_summary_and_keywords(content: str) -> (str, str):
    """Asks OpenAI for a summary and keywords."""
    if not content:
        return None, None

    prompt = f"""
    Voici un article. Analyse-le et fournis les éléments suivants :
    1.  Un résumé concis et neutre en {DEFAULT_LANGUAGE} d'environ {DEFAULT_SUMMARY_LENGTH} mots.
    2.  Une liste de {DEFAULT_KEYWORD_COUNT} mots-clés pertinents, séparés par des virgules.

    Le format de ta réponse DOIT être :
    RÉSUMÉ: [Ton résumé ici]
    MOTS-CLÉS: [Tes mots-clés ici]

    ARTICLE:
    {content[:8000]}
    """ # Truncate content to fit model context window

    try:
        response = await openai.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        raw_text = response.choices[0].message.content

        summary = raw_text.split("RÉSUMÉ:")[1].split("MOTS-CLÉS:")[0].strip()
        keywords = raw_text.split("MOTS-CLÉS:")[1].strip()
        return summary, keywords
    except Exception as e:
        logging.error(f"OpenAI API call failed: {e}")
        return None, None

async def process_feed(source: Source, db: Session):
    """Fetches a single RSS feed, processes entries, and saves them."""
    logging.info(f"Processing source: {source.name} ({source.url})")
    try:
        feed = feedparser.parse(source.url)
        if feed.bozo:
            raise ValueError(f"Feed parsing error: {feed.bozo_exception}")

        source.last_fetched_at = datetime.utcnow()

        for entry in feed.entries[:source.max_items]:
            article_url = entry.link

            # Check if article already exists
            existing_article = db.execute(select(Article).where(Article.url == article_url)).first()
            if existing_article:
                continue

            # Extract content
            content = entry.get("content", [{}])[0].get("value", entry.get("summary", ""))

            # Get summary and keywords from AI
            summary, keywords = await get_summary_and_keywords(content)

            if not summary:
                logging.warning(f"Could not generate summary for article: {entry.title}, saving without summary.")

            # Create new article
            new_article = Article(
                source_id=source.id,
                title=entry.title,
                url=article_url,
                published_at=parse_date(entry.published) if hasattr(entry, 'published') else datetime.utcnow(),
                content=content,
                summary=summary,
                keywords=keywords,
                language=DEFAULT_LANGUAGE,
            )
            db.add(new_article)
            logging.info(f"  -> Added article: {entry.title}")

        source.status = SourceStatusEnum.ACTIVE
        db.commit()

    except Exception as e:
        logging.error(f"Failed to process source {source.name}: {e}")
        source.status = SourceStatusEnum.ERROR
        db.commit()


async def main():
    """Main function to run the fetching process."""
    logging.info("Starting article fetching process...")
    db = SessionLocal()
    try:
        active_sources = db.execute(
            select(Source).where(Source.status == SourceStatusEnum.ACTIVE)
        ).scalars().all()

        tasks = [process_feed(source, db) for source in active_sources]
        await asyncio.gather(*tasks)

    finally:
        db.close()
    logging.info("Article fetching process finished.")

if __name__ == "__main__":
    # Ensure OPENAI_API_KEY is loaded, e.g., from .env file
    # from dotenv import load_dotenv
    # load_dotenv()
    asyncio.run(main())