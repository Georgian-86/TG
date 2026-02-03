import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
import os
from dotenv import load_dotenv

load_dotenv('.env')
db_url = os.getenv("DATABASE_URL")
print(f"Testing URL: {db_url}")

async def test():
    try:
        engine = create_async_engine(db_url)
        async with engine.connect() as conn:
            print("Successfully connected!")
        await engine.dispose()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())
