import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def test_db():
    db_url = os.getenv("DATABASE_URL")
    print(f"Connecting to {db_url.split('@')[-1]}...")
    
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    
    engine = create_async_engine(db_url)
    
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT email FROM users LIMIT 5"))
        print("Users found:")
        for row in result:
            print(row[0])
            
    await engine.dispose()

if __name__ == "__main__":
    if not os.getenv("DATABASE_URL"):
        print("DATABASE_URL not set")
        sys.exit(1)
    asyncio.run(test_db())
