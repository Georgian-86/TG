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

# List of columns to ensure exist in 'feedbacks' table
REQUIRED_COLUMNS = {
    # Column Name: SQL Type
    "raw_response": "JSON",
    "failure_details": "TEXT",
    "retry_frequency": "VARCHAR(50)",
    "speed_vs_others": "VARCHAR(50)",
    "workflow_satisfaction": "VARCHAR(50)",
    "confidence_impact": "VARCHAR(50)",
    "comparison_objective": "VARCHAR(50)",
    "technical_issues_details": "TEXT" # Note: schema maps this to technical_issues string, so maybe not needed in DB? 
                                       # Wait, API combines it. So no column needed.
                                       # But 'failure_details' etc ARE in model.
}

async def migrate():
    """Run database migration for missing feedback columns (Async)"""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--db-url", help="Database URL (overrides env var)", required=False)
    args = parser.parse_args()

    # STRICT PRIORITY: CLI Argument > Environment Variable > Settings
    db_url = args.db_url or os.getenv("DATABASE_URL")
    
    if not db_url:
        logger.warning("DATABASE_URL env var not set. Falling back to settings...")
        db_url = settings.DATABASE_URL

    if not db_url:
        logger.error("❌ ERROR: DATABASE_URL not set! Use --db-url or set DATABASE_URL env var.")
        return

    # MASK CREDENTIALS for logging
    safe_url = db_url.split('@')[-1] if '@' in db_url else 'LOCAL'
    logger.info(f"Target Database Host: {safe_url}")

    if "sqlite" in db_url or "test.db" in db_url:
        logger.error("❌ FATAL: Attempting to run PRODUCTION migration against SQLite.")
        logger.error("   Please use: python backend/migrate_feedback_full.py --db-url POSTRGRES_URL")
        return

    # Handle Railway/Heroku postgres:// -> postgresql+asyncpg://
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    
    # CRITICAL: Ensure we are using asyncpg for Postgres
    if "postgresql" in db_url and "asyncpg" not in db_url:
         db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
    
    logger.info(f"Final Connection String Scheme: {db_url.split(':')[0]}")

    engine = create_async_engine(db_url, echo=True)
    
    async with engine.begin() as conn:
        try:
            # Define sync function for inspection
            def get_existing_columns(connection):
                inspector = inspect(connection)
                return [c['name'] for c in inspector.get_columns('feedbacks')]

            # Run inspection synchronously
            existing_columns = await conn.run_sync(get_existing_columns)
            
            for col_name, col_type in REQUIRED_COLUMNS.items():
                if col_name not in existing_columns:
                    # Check if model actually has this column (technical_issues_details doesnt exist in model)
                    if col_name == "technical_issues_details": continue

                    logger.info(f"Adding missing column '{col_name}' ({col_type})...")
                    await conn.execute(text(f"ALTER TABLE feedbacks ADD COLUMN {col_name} {col_type}"))
                    logger.info(f"Column '{col_name}' added successfully.")
                else:
                    logger.info(f"Column '{col_name}' already exists.")
                    
        except Exception as e:
            logger.error(f"Error updating feedbacks table: {e}")
    
    await engine.dispose()
    logger.info("Feedback migration complete.")

if __name__ == "__main__":
    asyncio.run(migrate())
