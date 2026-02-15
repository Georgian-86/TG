import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text, inspect
import os
import sys

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def migrate():
    """Run database migration for raw_response column (Async)"""
    # Use DATABASE_URL from environment
    db_url = settings.DATABASE_URL
    if not db_url:
        logger.error("DATABASE_URL not set!")
        return

    logger.info(f"Connecting to database...")
    
    # Handle Railway/Heroku postgres:// -> postgresql+asyncpg://
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    
    engine = create_async_engine(db_url, echo=True)
    
    async with engine.begin() as conn:
        try:
            def check_column(connection):
                inspector = inspect(connection)
                columns = [c['name'] for c in inspector.get_columns('feedbacks')]
                return 'raw_response' in columns

            exists = await conn.run_sync(check_column)
            
            if not exists:
                logger.info("Adding raw_response column to feedbacks table...")
                await conn.execute(text("ALTER TABLE feedbacks ADD COLUMN raw_response JSON"))
                logger.info("Column added successfully.")
            else:
                logger.info("raw_response column already exists.")
                
        except Exception as e:
            logger.error(f"Error updating feedbacks table: {e}")
            # If table doesn't exist, it might fail, but usually feedbacks table exists by now
    
    await engine.dispose()
    logger.info("Migration complete.")

if __name__ == "__main__":
    asyncio.run(migrate())
