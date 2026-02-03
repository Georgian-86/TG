"""
Delete All Users from Database
Clean up all user records
"""
import asyncio
from sqlalchemy import delete
from app.database import AsyncSessionLocal
from app.models.user import User


async def delete_all_users():
    """Delete all users from database"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(delete(User))
        count = result.rowcount
        await db.commit()
        
        print(f"\n✅ Deleted {count} user(s) from database")
        return count


if __name__ == "__main__":
    print("\n🗑️  Deleting all users from database...")
    asyncio.run(delete_all_users())
    print("Database cleaned successfully!\n")
