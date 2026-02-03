import asyncio
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.user import User
from app.models.lesson_history import LessonHistory

async def check_history(email):
    async with AsyncSessionLocal() as session:
        # Find user
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user:
            print(f"User {email} not found")
            return

        print(f"User ID: {user.id}")

        # Find history
        result = await session.execute(select(LessonHistory).where(LessonHistory.user_id == user.id))
        history = result.scalars().all()
        
        print(f"Found {len(history)} history items:")
        for item in history:
            print(f" - [{item.created_at}] {item.topic} (ID: {item.id})")

if __name__ == "__main__":
    asyncio.run(check_history("optimus4586prime@gmail.com"))
