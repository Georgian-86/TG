"""Check specific lesson status"""
import asyncio
from app.models.lesson import Lesson
from app.database import AsyncSessionLocal
from sqlalchemy import select

async def check_lesson(lesson_id):
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Lesson).where(Lesson.id == lesson_id)
        )
        lesson = result.scalar_one_or_none()
        
        if lesson:
            print(f"Lesson ID: {lesson.id}")
            print(f"Topic: {lesson.topic}")
            print(f"Status: {lesson.status}")
            print(f"Error Message: {lesson.error_message}")
            print(f"Processing Time: {lesson.processing_time_seconds}s" if lesson.processing_time_seconds else "N/A")
            print(f"Sections: {len(lesson.lesson_plan) if lesson.lesson_plan else 0}")
            print(f"Quiz Questions: {len(lesson.quiz.get('questions', [])) if lesson.quiz else 0}")
            print(f"Created At: {lesson.created_at}")
            print(f"Completed At: {lesson.completed_at}")
        else:
            print("Lesson not found")

if __name__ == "__main__":
    import sys
    lesson_id = sys.argv[1] if len(sys.argv) > 1 else "719dc21e-553a-483b-87c9-60b69e75fca7"
    asyncio.run(check_lesson(lesson_id))
