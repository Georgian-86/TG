"""Check the failed lesson in database"""
import asyncio
from app.models.lesson import Lesson
from app.database import AsyncSessionLocal
from sqlalchemy import select

async def check_failed_lesson():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Lesson).order_by(Lesson.created_at.desc()).limit(1)
        )
        lesson = result.scalar_one_or_none()
        
        if lesson:
            print(f"Lesson ID: {lesson.id}")
            print(f"Topic: {lesson.topic}")
            print(f"Status: {lesson.status}")
            print(f"Error Message: {lesson.error_message}")
            print(f"Created At: {lesson.created_at}")
        else:
            print("No lessons found")

if __name__ == "__main__":
    asyncio.run(check_failed_lesson())
