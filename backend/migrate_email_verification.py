"""
Database Migration: Add Email Verification
Adds email_verified fields to users table and creates email_otps table
"""
import asyncio
from sqlalchemy import text
from app.database import engine
from app.models.email_otp import EmailOTP
from app.models.user import User
from app.database import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_migration():
    """Run migration to add email verification support"""
    
    async with engine.begin() as conn:
        logger.info("Starting email verification migration...")
        
        # Check if we're using SQLite or PostgreSQL
        result = await conn.execute(text("SELECT 1"))
        
        try:
            # Step 1: Add email verification columns to users table (if not exist)
            logger.info("Adding email_verified column to users table...")
            try:
                await conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN email_verified BOOLEAN DEFAULT FALSE NOT NULL
                """))
                logger.info("✓ Added email_verified column")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    logger.info("✓ email_verified column already exists")
                else:
                    raise
            
            logger.info("Adding email_verification_sent_at column to users table...")
            try:
                await conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN email_verification_sent_at TIMESTAMP
                """))
                logger.info("✓ Added email_verification_sent_at column")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    logger.info("✓ email_verification_sent_at column already exists")
                else:
                    raise
            
            # Step 2: Create email_otps table
            logger.info("Creating email_otps table...")
            await conn.run_sync(Base.metadata.create_all, tables=[EmailOTP.__table__])
            logger.info("✓ Created email_otps table")
            
            # Step 3: Set OAuth users as pre-verified (Google has verified their emails)
            logger.info("Setting OAuth users as email-verified...")
            result = await conn.execute(text("""
                UPDATE users 
                SET email_verified = TRUE 
                WHERE oauth_provider = 'google'
            """))
            logger.info(f"✓ Marked {result.rowcount} OAuth users as verified")
            
            logger.info("=" * 60)
            logger.info("Migration completed successfully!")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise


async def rollback_migration():
    """Rollback migration (for development/testing)"""
    
    async with engine.begin() as conn:
        logger.info("Rolling back email verification migration...")
        
        try:
            # Drop email_otps table
            logger.info("Dropping email_otps table...")
            await conn.execute(text("DROP TABLE IF EXISTS email_otps"))
            logger.info("✓ Dropped email_otps table")
            
            # Remove columns from users table
            # Note: SQLite doesn't support DROP COLUMN easily, so we skip for SQLite
            logger.info("Removing email verification columns from users table...")
            try:
                await conn.execute(text("ALTER TABLE users DROP COLUMN email_verified"))
                await conn.execute(text("ALTER TABLE users DROP COLUMN email_verification_sent_at"))
                logger.info("✓ Removed email verification columns")
            except Exception as e:
                logger.warning(f"Could not remove columns (SQLite limitation): {e}")
            
            logger.info("Rollback completed!")
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            raise


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        print("Running rollback...")
        asyncio.run(rollback_migration())
    else:
        print("Running migration...")
        asyncio.run(run_migration())
