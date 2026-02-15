"""
Migration Script: Update Subscription Tiers
----------------------------------------------
Migrates existing users from old tier names to new tier names:
  - basic -> silver
  - pro -> gold
  - enterprise -> institutional

Usage:
    python migrate_subscription_tiers.py
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_subscription_tiers():
    """Migrate subscription tiers from old naming to new naming"""
    try:
        # Create database engine
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        logger.info("Starting subscription tier migration...")
        
        # Migration mapping
        migrations = {
            "basic": "silver",
            "pro": "gold",
            "enterprise": "institutional"
        }
        
        total_updated = 0
        
        for old_tier, new_tier in migrations.items():
            # Update users with old tier names
            result = db.execute(
                text("""
                    UPDATE users 
                    SET subscription_tier = :new_tier 
                    WHERE subscription_tier = :old_tier
                """),
                {"old_tier": old_tier, "new_tier": new_tier}
            )
            
            count = result.rowcount
            if count > 0:
                logger.info(f"✅ Migrated {count} users from '{old_tier}' to '{new_tier}'")
                total_updated += count
            else:
                logger.info(f"ℹ️  No users found with tier '{old_tier}'")
        
        # Commit the changes
        db.commit()
        
        # Verify migration
        logger.info("\n📊 Post-migration tier distribution:")
        result = db.execute(
            text("SELECT subscription_tier, COUNT(*) as count FROM users GROUP BY subscription_tier")
        )
        
        for row in result:
            logger.info(f"  {row.subscription_tier}: {row.count} users")
        
        logger.info(f"\n✅ Migration completed successfully! Total users updated: {total_updated}")
        
        db.close()
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        raise


if __name__ == "__main__":
    migrate_subscription_tiers()
