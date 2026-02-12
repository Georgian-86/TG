import asyncio
from app.database import engine
from sqlalchemy import text

async def check_user_status():
    async with engine.begin() as conn:
        # Fetch the most recent user or specific user if known (using email if possible, or just first user)
        # Since I saw the ID in logs: 049173b2-ed04-4c64-9157-ef6ab216d70b
        user_id = '049173b2-ed04-4c64-9157-ef6ab216d70b' 
        print(f"Checking status for user: {user_id}")
        
        result = await conn.execute(text("SELECT id, email, feedback_provided FROM users WHERE id = :uid"), {"uid": user_id})
        user = result.fetchone()
        
        if user:
            print(f"User Found: {user.email}")
            print(f"Feedback Provided: {user.feedback_provided}")
        else:
            print("User not found.")

if __name__ == "__main__":
    asyncio.run(check_user_status())
