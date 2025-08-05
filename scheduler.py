# scheduler.py
import asyncio
import logging
from arq import create_pool
from arq.connections import RedisSettings
from sqlalchemy import select

from config import settings
from database import SessionLocal
from models import Source, SourceStatusEnum

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def main():
    """Trouve les sources actives et crée une tâche 'fetch_source' pour chacune."""
    logging.info("--- Starting Scheduler ---")
    redis_pool = await create_pool(RedisSettings(host=settings.REDIS_HOST, port=settings.REDIS_PORT))
    db = SessionLocal()
    try:
        active_sources = db.execute(select(Source).where(Source.status == SourceStatusEnum.ACTIVE)).scalars().all()
        logging.info(f"Found {len(active_sources)} active sources to schedule.")
        for source in active_sources:
            await redis_pool.enqueue_job('fetch_source', source.id)
            logging.info(f"Scheduled job for source: {source.name} (ID: {source.id})")
    finally:
        await redis_pool.close()
        db.close()
        logging.info("--- Scheduler Finished ---")

if __name__ == "__main__":
    asyncio.run(main())
