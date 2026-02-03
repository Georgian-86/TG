"""Get latest lesson error"""
import asyncio
from app.models.lesson import Lesson
from app.database import AsyncSessionLocal
from sqlalchemy import select

async def check():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Lesson).order_by(Lesson.created_at.desc()).limit(1)
        )
        lesson = result.scalar_one_or_none()
        if lesson:
            print(f"Lesson: {lesson.topic}")
            print(f"Status: {lesson.status}")
            print(f"Error: {lesson.error_message}")
        else:
            print("No lessons found")

asyncio.run(check())
