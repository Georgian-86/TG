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
import sqlite3
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_subscription_tiers():
    """Migrate subscription tiers from old naming to new naming"""
    try:
        # Connect directly to SQLite database
        db_path = os.path.join(os.path.dirname(__file__), "teachgenie.db")
        
        if not os.path.exists(db_path):
            logger.error(f"❌ Database not found at {db_path}")
            return
        
        logger.info(f"Connecting to database: {db_path}")
        db = sqlite3.connect(db_path)
        
        logger.info("Starting subscription tier migration...")
        
        cursor = db.cursor()
        
        # Migration mapping
        migrations = {
            "basic": "SILVER",
            "pro": "GOLD",
            "enterprise": "INSTITUTIONAL",
            "gold": "GOLD",  # Fix lowercase to uppercase
            "silver": "SILVER",  # Fix lowercase to uppercase
            "free": "FREE"  # Fix lowercase to uppercase
        }
        
        total_updated = 0
        
        for old_tier, new_tier in migrations.items():
            # Update users with old tier names
            cursor.execute(
                """
                UPDATE users 
                SET subscription_tier = ? 
                WHERE subscription_tier = ?
                """,
                (new_tier, old_tier)
            )
            
            count = cursor.rowcount
            if count > 0:
                logger.info(f"✅ Migrated {count} users from '{old_tier}' to '{new_tier}'")
                total_updated += count
            else:
                logger.info(f"ℹ️  No users found with tier '{old_tier}'")
        
        # Commit the changes
        db.commit()
        
        # Verify migration
        logger.info("\n📊 Post-migration tier distribution:")
        cursor.execute("SELECT subscription_tier, COUNT(*) as count FROM users GROUP BY subscription_tier")
        
        for row in cursor.fetchall():
            logger.info(f"  {row[0]}: {row[1]} users")
        
        logger.info(f"\n✅ Migration completed successfully! Total users updated: {total_updated}")
        
        cursor.close()
        db.close()
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        raise


if __name__ == "__main__":
    migrate_subscription_tiers()
