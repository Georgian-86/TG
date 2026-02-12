"""
Check production database tables
"""
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def check_tables():
    # Production database URL
    database_url = "postgresql+asyncpg://teachgenie_admin:4Q9QWxCUnbKAJC3@teachgenie-db.cklww4emo61g.us-east-1.rds.amazonaws.com:5432/teachgenie"
    
    engine = create_async_engine(database_url)
    
    try:
        async with engine.connect() as conn:
            # Get all tables
            result = await conn.execute(text("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public' 
                ORDER BY tablename
            """))
            tables = [row[0] for row in result]
            
            print("\n" + "=" * 60)
            print("PRODUCTION DATABASE TABLES")
            print("=" * 60)
            for table in tables:
                print(f"  ✓ {table}")
            print("=" * 60)
            print(f"\nTotal tables: {len(tables)}")
            
            # Check specifically for admin_logs
            if "admin_logs" in tables:
                print("\n✅ admin_logs table EXISTS in production")
                
                # Get row count
                result = await conn.execute(text("SELECT COUNT(*) FROM admin_logs"))
                count = result.scalar()
                print(f"   Rows in admin_logs: {count}")
                
                # Get table structure
                result = await conn.execute(text("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = 'admin_logs'
                    ORDER BY ordinal_position
                """))
                columns = result.fetchall()
                print(f"\n   Columns in admin_logs table:")
                for col in columns:
                    print(f"     - {col[0]}: {col[1]} (nullable: {col[2]})")
            else:
                print("\n❌ admin_logs table DOES NOT EXIST in production")
                print("   You need to run migrations to create it")
            
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_tables())
