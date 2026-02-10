"""
Initialize RDS PostgreSQL Database
Run this script ONCE to create all tables in your RDS database
"""
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Import all models to register with Base
from app.models import user, lesson, email_otp, lesson_history, feedback, admin_log, file_upload
from app.database import Base

async def init_rds():
    """Create all tables in RDS PostgreSQL"""
    
    # Get RDS connection string from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set!")
        print("Set it to your RDS connection string:")
        print("postgresql+asyncpg://username:password@teachgenie-db.xxx.rds.amazonaws.com:5432/teachgenie")
        return
    
    print(f"Connecting to RDS: {database_url[:50]}...")
    
    # Create engine
    engine = create_async_engine(database_url, echo=True)
    
    try:
        # Drop all tables first (CAUTION: This deletes all data!)
        print("\n⚠️  WARNING: This will DROP all existing tables and recreate them!")
        confirm = input("Type 'YES' to continue: ")
        if confirm != "YES":
            print("Aborted.")
            return
        
        async with engine.begin() as conn:
            print("\n🗑️  Dropping all tables...")
            await conn.run_sync(Base.metadata.drop_all)
            print("✅ Tables dropped")
            
            print("\n🔨 Creating all tables...")
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Tables created")
            
            # Verify tables exist
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = [row[0] for row in result]
            print(f"\n📋 Created tables: {', '.join(tables)}")
        
        print("\n✅ Database initialization complete!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    print("=" * 60)
    print("RDS PostgreSQL Database Initializer")
    print("=" * 60)
    asyncio.run(init_rds())
