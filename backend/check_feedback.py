import asyncio
from app.database import engine
from sqlalchemy import text

async def check_feedback_count():
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT COUNT(*) FROM feedbacks"))
        count = result.scalar()
        print(f"Feedback Count: {count}")

if __name__ == "__main__":
    asyncio.run(check_feedback_count())
