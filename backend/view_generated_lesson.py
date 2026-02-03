"""View the successfully generated lesson from database"""
import asyncio
import json
from app.models.lesson import Lesson
from app.database import AsyncSessionLocal
from sqlalchemy import select

async def view_lesson():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Lesson).where(Lesson.topic == "Machine Learning Basics").order_by(Lesson.created_at.desc()).limit(1)
        )
        lesson = result.scalar_one_or_none()
        if lesson:
            print(f"Lesson ID: {lesson.id}")
            print(f"Topic: {lesson.topic}")
            print(f"Status: {lesson.status}")
            print(f"Processing Time: {lesson.processing_time_seconds}s")
            print(f"\nLesson Plan: {json.dumps(lesson.lesson_plan, indent=2) if lesson.lesson_plan else 'None'}")
            print(f"\nResources: {json.dumps(lesson.resources, indent=2) if lesson.resources else 'None'}")
            print(f"\nQuiz: {json.dumps(lesson.quiz, indent=2) if lesson.quiz else 'None'}")
            
            # Save to file
            data = {
                "id": lesson.id,
                "topic": lesson.topic,
                "level": str(lesson.level),
                "duration": lesson.duration,
                "status": str(lesson.status),
                "processing_time_seconds": lesson.processing_time_seconds,
                "lesson_plan": lesson.lesson_plan,
                "resources": lesson.resources,
                "quiz": lesson.quiz,
                "key_takeaways": lesson.key_takeaways
            }
            with open("generated_lesson.json", "w") as f:
                json.dump(data, f, indent=2, default=str)
            print(f"\n✅ Saved to generated_lesson.json")
        else:
            print("No lesson found")

asyncio.run(view_lesson())
