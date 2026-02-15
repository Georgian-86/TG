"""
Migrate Feedbacks Table on RDS PostgreSQL
Safely drops ONLY the feedbacks table and recreates it with the new schema.
Does NOT affect other tables (users, lessons, etc.)

Usage:
  DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname python migrate_feedback_rds.py
"""
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Import feedback model and Base
from app.models.feedback import Feedback
from app.database import Base

async def migrate_feedbacks():
    """Drop and recreate ONLY the feedbacks table on RDS"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set!")
        print("Set it to your RDS connection string:")
        print("  DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname python migrate_feedback_rds.py")
        return
    
    # Safety check: must be PostgreSQL
    if "sqlite" in database_url:
        print("This script is for RDS PostgreSQL only. Use recreate_feedback_table.py for local SQLite.")
        return
    
    print(f"Connecting to RDS: {database_url[:50]}...")
    
    engine = create_async_engine(database_url, echo=True)
    
    try:
        async with engine.begin() as conn:
            # Check if feedbacks table exists
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'feedbacks'
                )
            """))
            exists = result.scalar()
            
            if exists:
                print("\n⚠️  Dropping feedbacks table (other tables are NOT affected)...")
                await conn.run_sync(lambda sync_conn: Feedback.__table__.drop(sync_conn, checkfirst=True))
                print("✅ Feedbacks table dropped")
            else:
                print("ℹ️  Feedbacks table doesn't exist yet, creating fresh...")
            
            print("\n🔨 Creating feedbacks table with new schema...")
            await conn.run_sync(lambda sync_conn: Feedback.__table__.create(sync_conn, checkfirst=True))
            print("✅ Feedbacks table created with new schema")
            
            # Verify columns
            result = await conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'feedbacks' 
                ORDER BY ordinal_position
            """))
            columns = [(row[0], row[1]) for row in result]
            print(f"\n📋 Feedbacks table columns ({len(columns)}):")
            for name, dtype in columns:
                print(f"   - {name}: {dtype}")
        
        print("\n✅ RDS feedbacks migration complete!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    print("=" * 60)
    print("RDS Feedbacks Table Migration")
    print("(Only affects the feedbacks table)")
    print("=" * 60)
    asyncio.run(migrate_feedbacks())
