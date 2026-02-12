import asyncio
from app.database import engine
from sqlalchemy import text

async def reset_feedback_table():
    async with engine.begin() as conn:
        print("Dropping feedbacks table...")
        await conn.execute(text("DROP TABLE IF EXISTS feedbacks"))
        print("Table dropped.")

if __name__ == "__main__":
    asyncio.run(reset_feedback_table())
